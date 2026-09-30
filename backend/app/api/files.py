import mimetypes
from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from app.models.schemas import (
    FileNode,
    FileContentResponse,
    FileUpdateRequest,
    FileOperationResponse,
    FileConflictResponse
)
from app.workspace.manager import (
    workspace_manager,
    WorkspaceSecurityError,
    WorkspaceNotFoundError,
    FileConflictError
)
from app.agent.session_manager import session_manager
from app.agent.event_handler import EventNormalizer

router = APIRouter(prefix="/api/projects/{project_id}/files", tags=["files"])
preview_router = APIRouter(prefix="/api/projects/{project_id}/preview", tags=["preview"])


@preview_router.get("")
@preview_router.get("/{file_path:path}")
async def preview_workspace_file(project_id: str, file_path: str = "index.html"):
    """Serves raw static workspace files (HTML/CSS/JS) for live web app previews."""
    clean_path = file_path or "index.html"
    try:
        content, size, is_binary, version = await workspace_manager.read_file(project_id, clean_path)
        mime_type, _ = mimetypes.guess_type(clean_path)
        return Response(content=content, media_type=mime_type or "text/html")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[FileNode])
def list_files(project_id: str):
    """Retrieve the recursive file tree for a project workspace."""
    try:
        return workspace_manager.list_files_tree(project_id)
    except WorkspaceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{file_path:path}", response_model=FileContentResponse)
async def read_file(project_id: str, file_path: str):
    """Read contents and current version of a file in the project workspace."""
    try:
        content, size, is_binary, version = await workspace_manager.read_file(project_id, file_path)
        return FileContentResponse(
            path=file_path.replace("\\", "/"),
            content=content,
            size=size,
            is_binary=is_binary,
            version=version
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkspaceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{file_path:path}", response_model=FileOperationResponse)
async def update_file(project_id: str, file_path: str, payload: FileUpdateRequest):
    """Save/update file with optional version check. Prevents silent overwrite conflicts."""
    try:
        bytes_written, new_version = await workspace_manager.write_file(
            project_id=project_id,
            relative_path=file_path,
            content=payload.content,
            expected_version=payload.expected_version,
            user_id=payload.user_id
        )

        await session_manager.broadcast_event(
            project_id,
            EventNormalizer.file_changed(project_id=project_id, path=file_path, version=new_version)
        )

        return FileOperationResponse(
            success=True,
            path=file_path.replace("\\", "/"),
            message=f"Successfully saved {bytes_written} bytes",
            version=new_version
        )
    except FileConflictError as e:
        await session_manager.broadcast_event(
            project_id,
            EventNormalizer.file_conflict(
                project_id=project_id,
                path=e.path,
                server_version=e.server_version,
                expected_version=e.expected_version,
                server_content=e.server_content
            )
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "conflict": True,
                "path": e.path,
                "server_version": e.server_version,
                "expected_version": e.expected_version,
                "server_content": e.server_content,
                "message": str(e)
            }
        )
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkspaceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{file_path:path}", response_model=FileOperationResponse)
async def delete_file(project_id: str, file_path: str):
    """Delete a file or folder in the project workspace."""
    try:
        deleted = workspace_manager.delete_file(project_id, file_path)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        await session_manager.broadcast_event(
            project_id,
            EventNormalizer.file_deleted(project_id=project_id, path=file_path)
        )

        return FileOperationResponse(
            success=True,
            path=file_path.replace("\\", "/"),
            message="File deleted successfully"
        )
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkspaceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    FileNode,
    FileContentResponse,
    FileUpdateRequest,
    FileOperationResponse
)
from app.workspace.manager import (
    workspace_manager,
    WorkspaceSecurityError,
    WorkspaceNotFoundError
)

router = APIRouter(prefix="/api/projects/{project_id}/files", tags=["files"])


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
    """Read contents of a file inside the project workspace."""
    try:
        content, size, is_binary = await workspace_manager.read_file(project_id, file_path)
        return FileContentResponse(
            path=file_path.replace("\\", "/"),
            content=content,
            size=size,
            is_binary=is_binary
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
    """Save/update contents of a file in the project workspace."""
    try:
        bytes_written = await workspace_manager.write_file(project_id, file_path, payload.content)
        return FileOperationResponse(
            success=True,
            path=file_path.replace("\\", "/"),
            message=f"Successfully wrote {bytes_written} bytes"
        )
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkspaceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{file_path:path}", response_model=FileOperationResponse)
def delete_file(project_id: str, file_path: str):
    """Delete a file or folder in the project workspace."""
    try:
        deleted = workspace_manager.delete_file(project_id, file_path)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
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

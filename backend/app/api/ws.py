import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.agent.session_manager import session_manager
from app.workspace.manager import WorkspaceSecurityError

router = APIRouter(tags=["websocket"])
logger = logging.getLogger("summit.ws")


@router.websocket("/api/projects/{project_id}/agent/stream")
async def agent_event_stream(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint that streams real-time Summit agent events,
    tool calls, terminal logs, file updates, and reasoning states to the UI.
    """
    await websocket.accept()
    logger.info(f"WebSocket client connected for project: {project_id}")

    try:
        # Register connection in session manager
        await session_manager.register_connection(project_id, websocket)

        # Keep connection open and handle incoming ping / client messages
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # Handle client ping or client-initiated actions
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for project: {project_id}")
    except Exception as e:
        logger.error(f"WebSocket error for project {project_id}: {e}")
    finally:
        await session_manager.unregister_connection(project_id, websocket)

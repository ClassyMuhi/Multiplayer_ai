import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.agent.session_manager import session_manager

router = APIRouter(tags=["websocket"])
logger = logging.getLogger("summit.ws")


@router.websocket("/api/projects/{project_id}/agent/stream")
async def agent_event_stream(
    websocket: WebSocket,
    project_id: str,
    user_id: Optional[str] = Query(None),
    display_name: Optional[str] = Query(None)
):
    """
    WebSocket endpoint streaming real-time Summit events, tool calls, terminal logs,
    file updates, memory updates, and user presence to all project collaborators.
    """
    await websocket.accept()

    uid = user_id or f"user_{id(websocket)}"
    name = display_name or f"User-{uid[:4]}"

    logger.info(f"WebSocket client connected: {name} ({uid}) for project: {project_id}")

    try:
        await session_manager.register_connection(project_id, websocket, user_id=uid, display_name=name)

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {name} for project: {project_id}")
    except Exception as e:
        logger.error(f"WebSocket error for project {project_id}: {e}")
    finally:
        await session_manager.unregister_connection(project_id, websocket)

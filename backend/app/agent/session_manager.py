import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Set, Optional, List, Tuple
from fastapi import WebSocket

from app.models.schemas import (
    AgentStatusType,
    AgentSessionStatus,
    AppEvent,
    AppEventType,
    UserPresenceInfo
)
from app.agent.event_handler import EventNormalizer
from app.database.repository import repository

logger = logging.getLogger("summit.session_manager")


class SessionManager:
    """
    Manages active Summit agent sessions and WebSocket room connections per project.
    Supports real-time multiplayer presence, shared agent streaming, and pause/resume execution states.
    """

    def __init__(self):
        # project_id -> dict of websocket -> (user_id, display_name)
        self._connections: Dict[str, Dict[WebSocket, Tuple[str, str]]] = {}
        # project_id -> current AgentStatusType
        self._status: Dict[str, AgentStatusType] = {}
        # project_id -> asyncio.Task for active execution
        self._running_tasks: Dict[str, asyncio.Task] = {}
        # project_id -> asyncio.Event for pause/resume control
        self._pause_events: Dict[str, asyncio.Event] = {}
        # project_id -> list of active tools
        self._active_tools: Dict[str, list] = {}
        # Lock for thread safety
        self._lock = asyncio.Lock()

    async def register_connection(self, project_id: str, websocket: WebSocket, user_id: str, display_name: str):
        repository.get_or_create_user(user_id, display_name)

        async with self._lock:
            if project_id not in self._connections:
                self._connections[project_id] = {}
            self._connections[project_id][websocket] = (user_id, display_name)

        # Build list of connected users
        users_list = self.get_connected_users(project_id)

        # Broadcast USER_JOINED event
        joined_evt = EventNormalizer.user_joined(
            project_id=project_id,
            user_id=user_id,
            display_name=display_name,
            connected_users=[u.model_dump() for u in users_list]
        )
        await self.broadcast_event(project_id, joined_evt)

        # Send initial status event to newly connected client
        current_status = self.get_status(project_id)
        status_event = EventNormalizer.agent_status(
            project_id=project_id,
            status=current_status.status,
            message=f"Connected as {display_name}"
        )
        try:
            await websocket.send_text(status_event.model_dump_json())
        except Exception as e:
            logger.warning(f"Failed to send initial status event: {e}")

    async def unregister_connection(self, project_id: str, websocket: WebSocket):
        user_info = None
        async with self._lock:
            if project_id in self._connections and websocket in self._connections[project_id]:
                user_info = self._connections[project_id].pop(websocket)
                if not self._connections[project_id]:
                    del self._connections[project_id]

        if user_info:
            user_id, display_name = user_info
            users_list = self.get_connected_users(project_id)
            left_evt = EventNormalizer.user_left(
                project_id=project_id,
                user_id=user_id,
                display_name=display_name,
                connected_users=[u.model_dump() for u in users_list]
            )
            await self.broadcast_event(project_id, left_evt)

    def get_connected_users(self, project_id: str) -> List[UserPresenceInfo]:
        room = self._connections.get(project_id, {})
        seen = set()
        result = []
        for ws, (uid, name) in room.items():
            if uid not in seen:
                seen.add(uid)
                result.append(UserPresenceInfo(
                    user_id=uid,
                    display_name=name,
                    connected_at=datetime.now(timezone.utc)
                ))
        return result

    async def broadcast_event(self, project_id: str, event: AppEvent):
        json_payload = event.model_dump_json()

        if event.type == AppEventType.AGENT_STATUS:
            status_val = event.data.get("status")
            if status_val:
                try:
                    self._status[project_id] = AgentStatusType(status_val)
                except ValueError:
                    pass

        room = self._connections.get(project_id, {})
        if not room:
            return

        dead_connections = []
        for ws in list(room.keys()):
            try:
                await ws.send_text(json_payload)
            except Exception:
                dead_connections.append(ws)

        if dead_connections:
            async with self._lock:
                for dead_ws in dead_connections:
                    if project_id in self._connections:
                        self._connections[project_id].pop(dead_ws, None)

    def get_status(self, project_id: str) -> AgentSessionStatus:
        status = self._status.get(project_id, AgentStatusType.IDLE)
        active_tools = self._active_tools.get(project_id, [])
        return AgentSessionStatus(
            project_id=project_id,
            status=status,
            active_tools=active_tools,
            updated_at=datetime.now(timezone.utc)
        )

    def set_status(self, project_id: str, status: AgentStatusType):
        self._status[project_id] = status

    def is_running(self, project_id: str) -> bool:
        task = self._running_tasks.get(project_id)
        return task is not None and not task.done()

    def set_running_task(self, project_id: str, task: asyncio.Task):
        self._running_tasks[project_id] = task
        event = asyncio.Event()
        event.set()
        self._pause_events[project_id] = event

    async def check_pause(self, project_id: str):
        """Called inside agent loop to pause execution if paused."""
        evt = self._pause_events.get(project_id)
        if evt:
            await evt.wait()

    def pause_session(self, project_id: str) -> bool:
        evt = self._pause_events.get(project_id)
        if evt and self.is_running(project_id):
            evt.clear()
            self._status[project_id] = AgentStatusType.PAUSED
            return True
        return False

    def resume_session(self, project_id: str) -> bool:
        evt = self._pause_events.get(project_id)
        if evt and self.is_running(project_id):
            evt.set()
            self._status[project_id] = AgentStatusType.EXECUTING
            return True
        return False

    def stop_session(self, project_id: str) -> bool:
        task = self._running_tasks.get(project_id)
        evt = self._pause_events.get(project_id)
        if evt:
            evt.set()  # Unblock if paused before cancelling
        if task and not task.done():
            task.cancel()
            self._status[project_id] = AgentStatusType.IDLE
            return True
        return False


session_manager = SessionManager()

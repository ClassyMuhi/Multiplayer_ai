import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Set, Optional
from fastapi import WebSocket


from app.models.schemas import (
    AgentStatusType,
    AgentSessionStatus,
    AppEvent,
    AppEventType
)
from app.agent.event_handler import EventNormalizer

logger = logging.getLogger("summit.session_manager")


class SessionManager:
    """
    Manages active Summit agent sessions and WebSocket subscribers per project.
    One project = One active Summit agent session.
    """

    def __init__(self):
        # project_id -> set of active WebSocket connections
        self._connections: Dict[str, Set[WebSocket]] = {}
        # project_id -> current AgentStatusType
        self._status: Dict[str, AgentStatusType] = {}
        # project_id -> asyncio.Task for active execution
        self._running_tasks: Dict[str, asyncio.Task] = {}
        # project_id -> list of active tools
        self._active_tools: Dict[str, list] = {}
        # Lock for thread safety
        self._lock = asyncio.Lock()

    async def register_connection(self, project_id: str, websocket: WebSocket):
        async with self._lock:
            if project_id not in self._connections:
                self._connections[project_id] = set()
            self._connections[project_id].add(websocket)

        # Send initial status event to newly connected client
        current_status = self.get_status(project_id)
        status_event = EventNormalizer.agent_status(
            project_id=project_id,
            status=current_status.status,
            message="Connected to Summit Agent stream"
        )
        try:
            await websocket.send_text(status_event.model_dump_json())
        except Exception as e:
            logger.warning(f"Failed to send initial status event: {e}")

    async def unregister_connection(self, project_id: str, websocket: WebSocket):
        async with self._lock:
            if project_id in self._connections:
                self._connections[project_id].discard(websocket)
                if not self._connections[project_id]:
                    del self._connections[project_id]

    async def broadcast_event(self, project_id: str, event: AppEvent):
        """Broadcasts a normalized AppEvent to all connected clients for a project."""
        json_payload = event.model_dump_json()

        # Update cached status if status event
        if event.type == AppEventType.AGENT_STATUS:
            status_val = event.data.get("status")
            if status_val:
                try:
                    self._status[project_id] = AgentStatusType(status_val)
                except ValueError:
                    pass

        connections = list(self._connections.get(project_id, set()))
        if not connections:
            return

        dead_connections = []
        for ws in connections:
            try:
                await ws.send_text(json_payload)
            except Exception:
                dead_connections.append(ws)

        if dead_connections:
            async with self._lock:
                for dead_ws in dead_connections:
                    if project_id in self._connections:
                        self._connections[project_id].discard(dead_ws)

    def get_status(self, project_id: str) -> AgentSessionStatus:
        """Returns the current agent session status for a project."""
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

    def stop_session(self, project_id: str) -> bool:
        """Stops/cancels the active agent task for a project."""
        task = self._running_tasks.get(project_id)
        if task and not task.done():
            task.cancel()
            self._status[project_id] = AgentStatusType.IDLE
            return True
        return False


session_manager = SessionManager()

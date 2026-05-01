import asyncio
import json
import logging
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["trace"])

class TraceConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Trace WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Trace WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast_event(self, event_data: dict):
        if not self.active_connections:
            return
            
        message = json.dumps(event_data)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                disconnected.append(connection)
                
        for conn in disconnected:
            self.disconnect(conn)

manager = TraceConnectionManager()

@router.websocket("/trace")
async def websocket_trace_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't really expect client to send much, but keep connection alive
            data = await websocket.receive_text()
            # Could handle client commands here
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def emit_trace(agent_name: str, status: str, message: str, details: dict = None):
    """
    Utility function to broadcast a trace event to all connected UI clients.
    """
    event = {
        "agent": agent_name,
        "status": status,
        "message": message,
        "details": details or {}
    }
    await manager.broadcast_event(event)

from fastapi import WebSocket
from typing import Dict, List

class WebSocketManager:
    def __init__(self):
        # Store active connections: {client_id: [websocket]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)

    def disconnect(self, websocket: WebSocket, client_id: int):
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]

    async def send_message_to_client(self, client_id: int, message: dict):
        if client_id in self.active_connections:
            for websocket in self.active_connections[client_id]:
                await websocket.send_json(message)

    async def broadcast_to_all(self, message: dict):
        for client_id in self.active_connections:
            for websocket in self.active_connections[client_id]:
                await websocket.send_json(message)

# Global instance
manager = WebSocketManager()
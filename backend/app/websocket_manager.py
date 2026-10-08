import json
import logging
from typing import Dict, List, Any
from fastapi import WebSocket

logger = logging.getLogger("dns_monitoring.websocket")

class ConnectionManager:
    def __init__(self):
        # Map network_id -> list of connected WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Global broadcast connections (e.g. super admin)
        self.global_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, network_id: str = "all"):
        await websocket.accept()
        if network_id == "all":
            self.global_connections.append(websocket)
        else:
            if network_id not in self.active_connections:
                self.active_connections[network_id] = []
            self.active_connections[network_id].append(websocket)
        logger.info(f"WebSocket client connected to channel: {network_id}")

    def disconnect(self, websocket: WebSocket, network_id: str = "all"):
        if network_id == "all":
            if websocket in self.global_connections:
                self.global_connections.remove(websocket)
        else:
            if network_id in self.active_connections and websocket in self.active_connections[network_id]:
                self.active_connections[network_id].remove(websocket)
        logger.info(f"WebSocket client disconnected from channel: {network_id}")

    async def broadcast_dns_log(self, network_id: str, log_data: Dict[str, Any]):
        message_json = json.dumps({"event": "dns_query", "data": log_data}, default=str)
        
        # Send to specific network subscribers
        if network_id in self.active_connections:
            for connection in list(self.active_connections[network_id]):
                try:
                    await connection.send_text(message_json)
                except Exception:
                    self.disconnect(connection, network_id)
                    
        # Send to global listeners
        for connection in list(self.global_connections):
            try:
                await connection.send_text(message_json)
            except Exception:
                self.disconnect(connection, "all")

    async def broadcast_threat_alert(self, network_id: str, alert_data: Dict[str, Any]):
        message_json = json.dumps({"event": "threat_alert", "data": alert_data}, default=str)
        
        if network_id in self.active_connections:
            for connection in list(self.active_connections[network_id]):
                try:
                    await connection.send_text(message_json)
                except Exception:
                    self.disconnect(connection, network_id)
                    
        for connection in list(self.global_connections):
            try:
                await connection.send_text(message_json)
            except Exception:
                self.disconnect(connection, "all")

    async def broadcast_device_update(self, network_id: str, device_data: Dict[str, Any]):
        message_json = json.dumps({"event": "device_update", "data": device_data}, default=str)
        if network_id in self.active_connections:
            for connection in list(self.active_connections[network_id]):
                try:
                    await connection.send_text(message_json)
                except Exception:
                    self.disconnect(connection, network_id)
        for connection in list(self.global_connections):
            try:
                await connection.send_text(message_json)
            except Exception:
                self.disconnect(connection, "all")

ws_manager = ConnectionManager()

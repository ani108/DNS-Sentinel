"""WebSocket handler for live DNS traffic streaming."""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis
from app.core.redis import RedisManager
from app.core.constants import REDIS_LIVE_TRAFFIC_CHANNEL
from app.core.logging import logger

router = APIRouter()


class TrafficStreamManager:
    """Manages WebSocket connections for live traffic streaming."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: str) -> None:
        """Send message to all connected WebSocket clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.active_connections.remove(conn)


manager = TrafficStreamManager()


async def redis_subscriber() -> None:
    """Background task: subscribe to Redis Pub/Sub and broadcast to WebSockets."""
    while True:
        try:
            redis_client = RedisManager.get_client()
            pubsub = redis_client.pubsub()
            await pubsub.subscribe(REDIS_LIVE_TRAFFIC_CHANNEL)
            
            logger.info("Redis Pub/Sub subscriber started for live traffic")
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    
                    # 1. Broadcast to UI
                    await manager.broadcast(data)
                    
                    # 2. Save to Database for Analytics
                    import json
                    from app.db.session import async_session_factory
                    from app.db.crud import DNSQueryCRUD
                    try:
                        event = json.loads(data)
                        async with async_session_factory() as session:
                            await DNSQueryCRUD.create(
                                session,
                                domain=event["domain"],
                                query_type=event["query_type"],
                                client_ip=event["client_ip"],
                                verdict=event["verdict"],
                                block_reason=event.get("block_reason"),
                                is_tunneling=(str(event.get("block_reason") or "").lower() == "tunneling"),
                            )
                            await session.commit()
                    except Exception as e:
                        logger.error(f"DB log error: {e}")
                    
        except Exception as e:
            logger.error(f"Redis subscriber error: {e}")
            await asyncio.sleep(2)  # Reconnect after 2 seconds


@router.websocket("/ws/traffic")
async def websocket_traffic(websocket: WebSocket):
    """WebSocket endpoint for live DNS traffic events."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; client can send ping/control messages
            data = await websocket.receive_text()
            # Echo back as acknowledgment
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

"""WebSocket live stream endpoint."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import json
import asyncio
from typing import Dict, Set
from datetime import datetime
import numpy as np
import base64
import cv2
import redis

from app.config import settings
from core.state.redis_state import StreamState, REDIS_AVAILABLE
from core.postprocess.heatmap import density_to_heatmap_image

router = APIRouter()

# Try to connect to Redis, but make it optional
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
except Exception as e:
    print(f"Warning: Redis not available for WebSocket: {e}")
    redis_client = None

# Active WebSocket connections
_active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, stream_id: str, websocket: WebSocket):
        """Connect a WebSocket client."""
        await websocket.accept()
        if stream_id not in self.connections:
            self.connections[stream_id] = set()
        self.connections[stream_id].add(websocket)
    
    def disconnect(self, stream_id: str, websocket: WebSocket):
        """Disconnect a WebSocket client."""
        if stream_id in self.connections:
            self.connections[stream_id].discard(websocket)
            if not self.connections[stream_id]:
                del self.connections[stream_id]
    
    async def broadcast(self, stream_id: str, message: dict):
        """Broadcast message to all clients for a stream."""
        if stream_id not in self.connections:
            return
        
        disconnected = set()
        for websocket in self.connections[stream_id]:
            try:
                await websocket.send_json(message)
            except:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        for ws in disconnected:
            self.disconnect(stream_id, ws)


manager = ConnectionManager()


def density_map_to_heatmap_image(density_map: np.ndarray, colormap: str = "JET", alpha: float = 0.55) -> str:
    """
    Convert density map to base64-encoded PNG image.
    
    Args:
        density_map: Density map (H, W)
        colormap: Colormap name (JET, VIRIDIS, etc.)
        alpha: Alpha blending factor
        
    Returns:
        Base64-encoded PNG image data URL
    """
    # Normalize to 0-1
    if density_map.max() > 0:
        normalized = density_map / density_map.max()
    else:
        normalized = density_map
    
    # Convert to 0-255
    normalized = (normalized * 255).astype(np.uint8)
    
    # Apply colormap
    colormap_code = getattr(cv2, f"COLORMAP_{colormap}", cv2.COLORMAP_JET)
    heatmap = cv2.applyColorMap(normalized, colormap_code)
    
    # Encode to PNG
    _, buffer = cv2.imencode('.png', heatmap)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return f"data:image/png;base64,{img_base64}"


@router.websocket("/streams/{stream_id}/live")
async def websocket_live(websocket: WebSocket, stream_id: str):
    """WebSocket endpoint for live stream updates."""
    await manager.connect(stream_id, websocket)
    
    try:
        # Subscribe to Redis pub/sub if available
        pubsub = None
        if redis_client:
            channel = f"{settings.REDIS_STREAM_PREFIX}:{stream_id}:live"
            pubsub = redis_client.pubsub()
            pubsub.subscribe(channel)
        
        # Also try to get latest stats
        stats = StreamState.get_stats(stream_id)
        if stats:
            message = {
                "type": "frame_stats",
                "ts": datetime.utcnow().timestamp(),
                "count": stats.get("count", 0),
                "zones": stats.get("zones", []),
                "fps": stats.get("fps", 0.0),
                "model": stats.get("model_used", "hybrid"),
                "heatmap": None,
            }
            await websocket.send_json(message)
        
        # Listen for updates
        while True:
            if pubsub:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    try:
                        data = json.loads(message["data"])
                        await websocket.send_json(data)
                    except Exception as e:
                        print(f"Error sending WebSocket message: {e}")
            else:
                # Fallback: send placeholder data if Redis not available
                message = {
                    "type": "frame_stats",
                    "ts": datetime.utcnow().timestamp(),
                    "count": 0,
                    "zones": [],
                    "fps": 0.0,
                    "model": "hybrid",
                    "heatmap": None,
                }
                await websocket.send_json(message)
                await asyncio.sleep(1.0)  # Slower updates without Redis
            
            # Small delay to prevent busy loop
            await asyncio.sleep(0.01)
    
    except WebSocketDisconnect:
        if pubsub:
            pubsub.close()
        manager.disconnect(stream_id, websocket)
    except Exception as e:
        if pubsub:
            pubsub.close()
        manager.disconnect(stream_id, websocket)
        print(f"WebSocket error: {e}")


async def publish_stream_update(stream_id: str, stats: dict, density_map: np.ndarray = None):
    """Publish stream update to WebSocket clients and Redis."""
    message = {
        "type": "frame_stats",
        "ts": datetime.utcnow().timestamp(),
        "count": stats.get("count", 0),
        "zones": [{"id": z["id"], "count": z["count"], "alert": z.get("alert", False)} 
                  for z in stats.get("zones", [])],
        "fps": stats.get("fps", 0.0),
        "model": stats.get("model_used", "unknown"),
        "heatmap": None,
    }
    
    # Add heatmap if provided
    if density_map is not None:
        message["heatmap"] = density_to_heatmap_image(density_map)
    
    # Publish to Redis pub/sub
    if redis_client:
        channel = f"{settings.REDIS_STREAM_PREFIX}:{stream_id}:live"
        redis_client.publish(channel, json.dumps(message))
    
    # Also broadcast directly to WebSocket clients
    await manager.broadcast(stream_id, message)


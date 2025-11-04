"""WebSocket live stream endpoint."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from uvicorn.protocols.utils import ClientDisconnected
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
from core.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Try to connect to Redis, but make it optional
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connected for WebSocket pub/sub")
except Exception as e:
    logger.warning(f"Redis not available for WebSocket: {e}. Using fallback mode.")
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
        logger.info(f"WebSocket connected for stream {stream_id} (total: {len(self.connections[stream_id])})")
    
    def disconnect(self, stream_id: str, websocket: WebSocket):
        """Disconnect a WebSocket client."""
        if stream_id in self.connections:
            self.connections[stream_id].discard(websocket)
            logger.info(f"WebSocket disconnected for stream {stream_id} (remaining: {len(self.connections[stream_id])})")
            if not self.connections[stream_id]:
                del self.connections[stream_id]
                logger.debug(f"Removed stream {stream_id} from connections")
    
    async def broadcast(self, stream_id: str, message: dict):
        """Broadcast message to all clients for a stream."""
        if stream_id not in self.connections:
            return
        
        disconnected = set()
        for websocket in list(self.connections[stream_id]):  # Create a copy to iterate safely
            try:
                await websocket.send_json(message)
            except (WebSocketDisconnect, ClientDisconnected, ConnectionError, RuntimeError) as e:
                # Client disconnected - remove from connections
                disconnected.add(websocket)
                logger.debug(f"Client disconnected during broadcast for stream {stream_id}: {type(e).__name__}")
            except Exception as e:
                # Other errors - log but don't remove (might be transient)
                logger.warning(f"Error sending to WebSocket for stream {stream_id}: {e}")
                disconnected.add(websocket)  # Remove on any error to be safe
        
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
    logger.info(f"WebSocket connection request for stream {stream_id}")
    await manager.connect(stream_id, websocket)
    
    pubsub = None
    try:
        # Subscribe to Redis pub/sub if available
        if redis_client:
            channel = f"{settings.REDIS_STREAM_PREFIX}:{stream_id}:live"
            logger.debug(f"Subscribing to Redis channel: {channel}")
            pubsub = redis_client.pubsub()
            pubsub.subscribe(channel)
            logger.info(f"Subscribed to Redis pub/sub for stream {stream_id}")
        else:
            logger.warning(f"Redis not available, using fallback mode for stream {stream_id}")
        
        # Also try to get latest stats
        try:
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
                    "frame": None,
                    "frame_url": None,
                    "status": "running",
                    "name": stream_id,
                }
                await websocket.send_json(message)
                logger.debug(f"Sent initial stats to WebSocket for stream {stream_id}")
        except (WebSocketDisconnect, ClientDisconnected, ConnectionError, RuntimeError):
            # Client already disconnected, exit gracefully
            raise
        except Exception as e:
            logger.warning(f"Error sending initial stats for stream {stream_id}: {e}")
        
        # Listen for updates
        message_count = 0
        while True:
            try:
                if pubsub:
                    message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message:
                        try:
                            data = json.loads(message["data"])
                            await websocket.send_json(data)
                            message_count += 1
                            if message_count % 30 == 0:
                                logger.debug(f"Sent {message_count} messages to WebSocket for stream {stream_id}")
                        except (WebSocketDisconnect, ClientDisconnected, ConnectionError, RuntimeError):
                            # Client disconnected, break out of loop
                            raise
                        except Exception as e:
                            # Only log if it's not a disconnection-related error
                            if not isinstance(e, (asyncio.CancelledError, ConnectionError)):
                                logger.debug(f"Error sending WebSocket message for stream {stream_id}: {e}")
                else:
                    # Fallback: send placeholder data if Redis not available
                    try:
                        message = {
                            "type": "frame_stats",
                            "ts": datetime.utcnow().timestamp(),
                            "count": 0,
                            "zones": [],
                            "fps": 0.0,
                            "model": "hybrid",
                            "heatmap": None,
                            "frame": None,
                            "frame_url": None,
                            "status": "running",
                            "name": stream_id,
                        }
                        await websocket.send_json(message)
                        await asyncio.sleep(1.0)  # Slower updates without Redis
                    except (WebSocketDisconnect, ClientDisconnected, ConnectionError, RuntimeError):
                        # Client disconnected, exit loop
                        raise
                
                # Small delay to prevent busy loop
                await asyncio.sleep(0.01)
            except (WebSocketDisconnect, ClientDisconnected, ConnectionError, RuntimeError):
                # Client disconnected, exit loop
                raise
    
    except (WebSocketDisconnect, ClientDisconnected):
        logger.info(f"WebSocket disconnected for stream {stream_id} (normal disconnect)")
        if pubsub:
            try:
                pubsub.close()
            except:
                pass
        manager.disconnect(stream_id, websocket)
    except ConnectionError as e:
        logger.info(f"WebSocket connection error for stream {stream_id}: {e}")
        if pubsub:
            try:
                pubsub.close()
            except:
                pass
        manager.disconnect(stream_id, websocket)
    except Exception as e:
        # Only log unexpected errors with full traceback
        # Skip logging for expected shutdown/disconnection errors
        if not isinstance(e, (RuntimeError, asyncio.CancelledError, ConnectionError, WebSocketDisconnect, ClientDisconnected)):
            logger.error(f"WebSocket error for stream {stream_id}: {e}", exc_info=True)
        elif not isinstance(e, (asyncio.CancelledError, RuntimeError)):
            # Log connection errors at info level, not error
            logger.debug(f"WebSocket connection error for stream {stream_id}: {type(e).__name__}")
        if pubsub:
            try:
                pubsub.close()
            except:
                pass
        manager.disconnect(stream_id, websocket)


async def publish_stream_update(stream_id: str, stats: dict, density_map: np.ndarray = None, frame_data: str = None):
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
        "frame": frame_data,
        "frame_url": frame_data,  # Alias for frontend compatibility
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


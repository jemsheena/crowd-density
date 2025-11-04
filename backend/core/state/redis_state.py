"""Redis state management for live stream stats."""
import redis
import json
from typing import Dict, Optional, Any
from datetime import datetime
from app.config import settings

# Try to connect to Redis, but make it optional
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"Warning: Redis not available: {e}. Using in-memory fallback.")
    REDIS_AVAILABLE = False
    redis_client = None
    # Fallback in-memory store
    _in_memory_store: Dict[str, Dict] = {}


class StreamState:
    """Manage stream state in Redis."""
    
    @staticmethod
    def _key(stream_id: str, field: str = None) -> str:
        """Generate Redis key."""
        base = f"{settings.REDIS_STREAM_PREFIX}:{stream_id}"
        return f"{base}:{field}" if field else base
    
    @staticmethod
    def update_stats(stream_id: str, stats: Dict[str, Any]):
        """Update stream statistics."""
        stats["updated_at"] = datetime.utcnow().isoformat()
        if REDIS_AVAILABLE and redis_client:
            key = StreamState._key(stream_id, "stats")
            redis_client.setex(key, 300, json.dumps(stats))  # 5 min TTL
        else:
            # Fallback to in-memory
            _in_memory_store[f"{stream_id}:stats"] = stats
    
    @staticmethod
    def get_stats(stream_id: str) -> Optional[Dict[str, Any]]:
        """Get current stream statistics."""
        if REDIS_AVAILABLE and redis_client:
            key = StreamState._key(stream_id, "stats")
            data = redis_client.get(key)
            if data:
                return json.loads(data)
        else:
            # Fallback to in-memory
            return _in_memory_store.get(f"{stream_id}:stats")
        return None
    
    @staticmethod
    def publish_update(stream_id: str, stats: Dict[str, Any], heatmap_data: str = None):
        """Publish stats update to Redis pub/sub."""
        if not REDIS_AVAILABLE or not redis_client:
            return  # Skip if Redis not available
        
        channel = StreamState._key(stream_id, "live")
        # Ensure stats are JSON-serializable
        import time
        updated_at = stats.get("updated_at")
        if isinstance(updated_at, str):
            # Try to convert to timestamp
            try:
                dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                ts = dt.timestamp()
            except:
                ts = time.time()
        else:
            ts = time.time()
        
        stats_copy = {
            "type": "frame_stats",
            "ts": ts,
            "count": stats.get("count", 0),
            "zones": stats.get("zones", []),
            "fps": stats.get("fps", 0.0),
            "model": stats.get("model_used", "unknown"),
            "heatmap": heatmap_data,
        }
        redis_client.publish(channel, json.dumps(stats_copy))
    
    @staticmethod
    def set_status(stream_id: str, status: str):
        """Set stream status."""
        if REDIS_AVAILABLE and redis_client:
            key = StreamState._key(stream_id, "status")
            redis_client.setex(key, 3600, status)  # 1 hour TTL
        else:
            # Fallback to in-memory
            _in_memory_store[f"{stream_id}:status"] = status
    
    @staticmethod
    def get_status(stream_id: str) -> Optional[str]:
        """Get stream status."""
        if REDIS_AVAILABLE and redis_client:
            key = StreamState._key(stream_id, "status")
            return redis_client.get(key)
        else:
            # Fallback to in-memory
            return _in_memory_store.get(f"{stream_id}:status")


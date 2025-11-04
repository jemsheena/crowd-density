"""Stream management routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime

from app.dto.streams import StreamCreate, StreamStats, StreamResponse, StreamListResponse
from app.config import settings
from app.services.stream_service import StreamService
from core.state.redis_state import StreamState

router = APIRouter()

# In-memory store for stream configs (replace with DB later)
_streams_db: dict[str, dict] = {}


@router.post("", response_model=StreamResponse, status_code=201)
async def create_stream(stream_data: StreamCreate):
    """Create a new stream."""
    try:
        # Create and start stream
        stream_id = await StreamService.create_stream(stream_data)
        
        # Store config
        _streams_db[stream_id] = {
            "id": stream_id,
            "name": stream_data.name,
            "source": stream_data.source.dict(),
            "inference": stream_data.inference.dict(),
            "zones": [z.dict() for z in stream_data.zones],
            "output": stream_data.output.dict() if stream_data.output else {},
            "status": "starting",
        }
        
        return StreamResponse(id=stream_id, status="starting")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create stream: {str(e)}")


@router.get("/{stream_id}/stats", response_model=StreamStats)
async def get_stream_stats(stream_id: str):
    """Get current statistics for a stream."""
    if stream_id not in _streams_db:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    # Fetch real stats from Redis
    stats = StreamState.get_stats(stream_id)
    
    if stats:
        # Convert zones to ZoneStats format
        zones = [
            {"id": z["id"], "count": z["count"], "alert": z.get("alert", False)}
            for z in stats.get("zones", [])
        ]
        
        return StreamStats(
            id=stream_id,
            count=stats.get("count", 0),
            fps=stats.get("fps", 0.0),
            latency_ms=stats.get("latency_ms", 0.0),
            zones=zones,
            model_decision=stats.get("model_used", "hybrid"),
            updated_at=datetime.fromisoformat(stats["updated_at"]) if stats.get("updated_at") else datetime.utcnow(),
        )
    
    # Fallback if no stats yet
    return StreamStats(
        id=stream_id,
        count=0,
        fps=0.0,
        latency_ms=0.0,
        zones=[],
        model_decision="hybrid",
        updated_at=datetime.utcnow(),
    )


@router.get("", response_model=StreamListResponse)
async def list_streams():
    """List all streams."""
    streams = []
    for stream_id, stream in _streams_db.items():
        # Get real status from Redis
        status = StreamState.get_status(stream_id) or stream.get("status", "unknown")
        streams.append(StreamResponse(id=stream_id, status=status))
    
    return StreamListResponse(streams=streams, total=len(streams))


@router.delete("/{stream_id}", status_code=204)
async def delete_stream(stream_id: str):
    """Delete a stream."""
    if stream_id not in _streams_db:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    # Stop ingestion service
    await StreamService.stop_stream(stream_id)
    del _streams_db[stream_id]
    return None


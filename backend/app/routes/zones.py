"""Zone management routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{stream_id}")
async def get_zones(stream_id: str):
    """Get zones for a stream."""
    # TODO: Implement
    return {"zones": []}


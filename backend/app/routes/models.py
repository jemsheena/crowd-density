"""Model management routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_models():
    """List available models."""
    # TODO: Implement model registry
    return {"models": []}


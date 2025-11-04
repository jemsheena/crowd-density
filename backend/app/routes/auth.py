"""Authentication routes."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    """Login endpoint."""
    # TODO: Implement JWT auth
    return {"access_token": "placeholder", "token_type": "bearer"}


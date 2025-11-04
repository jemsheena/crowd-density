"""Dependencies for dependency injection."""
from fastapi import Depends, HTTPException, status
from typing import Optional
from app.config import settings

# TODO: Implement actual auth dependencies
async def get_current_user():
    """Get current authenticated user."""
    if settings.AUTH_DISABLED:
        return {"id": "dev_user", "role": "admin"}
    # TODO: Verify JWT token
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

async def get_current_user_optional() -> Optional[dict]:
    """Get current user if authenticated, else None."""
    if settings.AUTH_DISABLED:
        return {"id": "dev_user", "role": "admin"}
    return None


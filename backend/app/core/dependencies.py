"""
FastAPI dependencies for authentication and authorization.

Design: JWT token is extracted from the Authorization header (Bearer scheme).
The student's identity is ALWAYS extracted from the token — never from request body.
This prevents students from claiming to be someone else.
"""
import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_token
from app.db.session import get_db

# HTTPBearer scheme — expects "Authorization: Bearer <token>"
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency: Decode JWT and return the current user.
    Raises 401 if token is missing, invalid, or expired.
    Raises 403 if user is deactivated.
    """
    from app.models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch user from DB
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact administrator.",
        )

    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    """Dependency: Get current user, guaranteed to be active."""
    return current_user


class RoleChecker:
    """
    Dependency factory for role-based access control.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(RoleChecker(["admin", "super_admin"]))])
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user=Depends(get_current_user)):
        user_role = current_user.primary_role
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' is not permitted to access this resource. Required: {self.allowed_roles}",
            )
        return current_user


def require_roles(*roles: str):
    """Shorthand dependency factory for role checking."""
    return Depends(RoleChecker(list(roles)))


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None

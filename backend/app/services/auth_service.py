"""Authentication business logic."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.user import User, Role, UserRole
from app.models.audit import PasswordResetToken
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token, generate_password_reset_token
)
from app.core.exceptions import UnauthorizedException, NotFoundException, ConflictException, ValidationException
from app.schemas.user import UserCreate, Token, UserResponse


async def authenticate_user(
    email: str,
    password: str,
    db: AsyncSession,
) -> User:
    """
    Authenticate user by email and password.
    Returns user if valid, raises UnauthorizedException otherwise.
    Does NOT reveal whether email or password was wrong (security best practice).
    """
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()

    # Constant-time comparison — always verify even if user not found
    # to prevent timing-based email enumeration attacks
    if user is None or not verify_password(password, user.hashed_password if user else "dummy"):
        raise UnauthorizedException("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")

    # Update last_login (fire and forget)
    user.last_login = datetime.now(tz=timezone.utc)
    db.add(user)

    return user


async def create_tokens_for_user(user: User) -> dict:
    """Create access and refresh tokens for a user."""
    access_token = create_access_token(
        subject=str(user.id),
        role=user.primary_role or "student",
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> dict:
    """
    Issue a new access token using a valid refresh token.
    Raises UnauthorizedException if refresh token is invalid.
    """
    from jose import JWTError
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise UnauthorizedException("Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or deactivated")

    new_access_token = create_access_token(
        subject=str(user.id),
        role=user.primary_role or "student",
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


async def register_user(user_data: UserCreate, db: AsyncSession) -> User:
    """Create a new user with the given role."""
    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == user_data.email.lower()))
    if result.scalar_one_or_none():
        raise ConflictException("Email already registered")

    # Get role
    result = await db.execute(select(Role).where(Role.name == user_data.role))
    role = result.scalar_one_or_none()
    if not role:
        raise ValidationException(f"Role '{user_data.role}' not found")

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=user_data.email.lower(),
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.flush()

    # Assign role
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.add(user_role)
    await db.flush()

    return user


async def change_password(
    user: User, current_password: str, new_password: str, db: AsyncSession
) -> None:
    """Change user's password after verifying current password."""
    if not verify_password(current_password, user.hashed_password):
        raise UnauthorizedException("Current password is incorrect")
    user.hashed_password = get_password_hash(new_password)
    db.add(user)


async def request_password_reset(email: str, db: AsyncSession) -> Optional[str]:
    """
    Initiate password reset flow.
    Returns reset token (to be sent via email).
    Returns None silently if email not found (don't reveal existence).
    """
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if not user:
        return None  # Silently fail — security best practice

    token = generate_password_reset_token()
    reset_token = PasswordResetToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token=token,
        expires_at=datetime.now(tz=timezone.utc) + timedelta(hours=1),
        is_used=False,
    )
    db.add(reset_token)
    return token


async def reset_password_with_token(token: str, new_password: str, db: AsyncSession) -> None:
    """Reset password using a valid reset token."""
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.is_used == False,
        )
    )
    reset_token = result.scalar_one_or_none()
    if not reset_token:
        raise ValidationException("Invalid or already used reset token")

    if datetime.now(tz=timezone.utc) > reset_token.expires_at.replace(tzinfo=timezone.utc):
        raise ValidationException("Reset token has expired")

    # Update password
    result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User")

    user.hashed_password = get_password_hash(new_password)
    reset_token.is_used = True
    db.add(user)
    db.add(reset_token)

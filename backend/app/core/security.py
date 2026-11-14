"""
Security utilities for SmartAttend.

Responsibilities:
- Password hashing/verification using bcrypt
- JWT access and refresh token generation/decoding
- Cryptographically secure QR token generation
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# bcrypt password hashing — cost factor 12 for good security/performance balance
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def get_password_hash(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    role: str,
    additional_claims: Optional[dict] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: User ID (UUID as string)
        role: User's primary role (e.g. "faculty")
        additional_claims: Optional extra JWT claims

    Returns:
        Signed JWT string
    """
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(tz=timezone.utc),
        "type": "access",
    }
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> str:
    """
    Create a JWT refresh token (longer-lived, used only to get new access tokens).

    Args:
        subject: User ID (UUID as string)

    Returns:
        Signed JWT string
    """
    expire = datetime.now(tz=timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(tz=timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Raises:
        JWTError: If token is invalid, expired, or tampered.

    Returns:
        Token payload dict
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Token validation failed: {str(e)}")


def generate_qr_token() -> str:
    """
    Generate a cryptographically secure QR token.

    Uses secrets.token_urlsafe which generates random bytes from os.urandom()
    (cryptographically secure random number generator).

    32 bytes = 256 bits of entropy — practically impossible to guess or brute-force.

    Returns:
        URL-safe base64-encoded token string (~43 chars)
    """
    return secrets.token_urlsafe(32)


def generate_password_reset_token() -> str:
    """Generate a secure password reset token."""
    return secrets.token_urlsafe(32)

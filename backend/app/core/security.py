"""
app/core/security.py

JWT token creation and verification.
Password hashing with bcrypt.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Return bcrypt hash of the password."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain_password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: Usually the user's UUID as a string.
        expires_delta: Custom expiry window; defaults to settings value.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode and validate a JWT.

    Returns:
        The subject (user UUID) if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload.get("sub")
    except JWTError:
        return None

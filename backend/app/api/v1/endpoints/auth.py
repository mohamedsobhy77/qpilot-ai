"""
app/api/v1/endpoints/auth.py

Authentication endpoints:
  POST /api/v1/auth/register  — Create account
  POST /api/v1/auth/login     — Get JWT token
  GET  /api/v1/auth/profile   — Get current user info
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.exceptions import ConflictError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    APIResponse,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account.
    Email must be unique. Password is bcrypt-hashed.
    """
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email '{payload.email}' already exists.",
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.flush()   # Get the UUID before commit

    return APIResponse(
        success=True,
        message="Account created successfully.",
        data=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate with email + password.
    Returns a JWT Bearer token on success.
    """
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.get("/profile", response_model=APIResponse)
async def profile(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return APIResponse(
        success=True,
        message="Profile retrieved.",
        data=UserResponse.model_validate(current_user),
    )

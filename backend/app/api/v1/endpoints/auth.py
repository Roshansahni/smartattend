"""Authentication endpoints."""
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import (
    LoginRequest, Token, RefreshTokenRequest,
    ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest,
    UserCreate, UserResponse
)
from app.schemas.common import MessageResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(
        email=credentials.email,
        password=credentials.password,
        db=db,
    )
    tokens = await auth_service.create_tokens_for_user(user)
    user_response = UserResponse.model_validate(user)
    return Token(**tokens, user=user_response)

@router.post("/refresh")
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh_access_token(body.refresh_token, db)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register_user(user_data, db)
    return UserResponse.model_validate(user)

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.request_password_reset(body.email, db)
    return MessageResponse(message="If that email exists, a reset link has been sent.")

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.reset_password_with_token(body.token, body.new_password, db)
    return MessageResponse(message="Password reset successfully")

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.change_password(
        user=current_user,
        current_password=body.current_password,
        new_password=body.new_password,
        db=db,
    )
    return MessageResponse(message="Password changed successfully")

@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

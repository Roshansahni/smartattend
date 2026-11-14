"""User management endpoints."""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.get("", response_model=list[UserResponse], dependencies=[Depends(admin_only)])
@router.get("/", response_model=list[UserResponse], dependencies=[Depends(admin_only)], include_in_schema=False)
async def list_all_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User))
    return [UserResponse.model_validate(u) for u in res.scalars().all()]

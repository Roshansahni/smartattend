"""Analytics endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])
admin_or_faculty = RoleChecker(["admin", "super_admin", "faculty"])

@router.get("/dashboard", dependencies=[Depends(admin_or_faculty)])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    return await analytics_service.get_admin_dashboard_stats(db)

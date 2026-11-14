"""Faculty management endpoints."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.schemas.faculty import FacultyCreate, FacultyResponse
from app.services import faculty_service

router = APIRouter(prefix="/faculty", tags=["Faculty"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.post("/", response_model=FacultyResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
async def create_faculty(data: FacultyCreate, db: AsyncSession = Depends(get_db)):
    return await faculty_service.create_faculty(data, db)

@router.get("/", dependencies=[Depends(admin_only)])
async def list_faculty(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await faculty_service.list_faculty(db, page, page_size)

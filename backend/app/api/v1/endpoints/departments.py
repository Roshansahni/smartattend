"""Departments endpoints."""
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.models.institution import Department
from app.schemas.course import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["Departments"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)], include_in_schema=False)
async def create_department(data: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    dept = Department(id=uuid.uuid4(), name=data.name, code=data.code.upper(), description=data.description, is_active=True)
    db.add(dept)
    await db.flush()
    return dept

@router.get("", response_model=list[DepartmentResponse])
@router.get("/", response_model=list[DepartmentResponse], include_in_schema=False)
async def list_departments(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Department).where(Department.is_active == True))
    return res.scalars().all()

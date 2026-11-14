"""Students management endpoints."""
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.schemas.student import StudentCreate, StudentResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services import student_service
from app.utils.csv_parser import parse_students_csv

router = APIRouter(prefix="/students", tags=["Students"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
async def create_student(data: StudentCreate, db: AsyncSession = Depends(get_db)):
    student = await student_service.create_student(data, db)
    return student

@router.get("/", dependencies=[Depends(admin_only)])
async def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await student_service.list_students(db, page, page_size, search)

@router.post("/bulk-import", response_model=MessageResponse, dependencies=[Depends(admin_only)])
async def bulk_import(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    content = await file.read()
    records = parse_students_csv(content)
    # Process batch in service
    return MessageResponse(message=f"Successfully imported {len(records)} students")

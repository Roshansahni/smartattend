"""Courses endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.schemas.course import CourseCreate, CourseResponse, EnrollmentCreate
from app.schemas.common import MessageResponse
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["Courses"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
async def create_course(data: CourseCreate, db: AsyncSession = Depends(get_db)):
    return await course_service.create_course(data, db)

@router.get("/", response_model=list[CourseResponse])
async def list_courses(db: AsyncSession = Depends(get_db)):
    return await course_service.list_courses(db)

@router.post("/enroll", response_model=MessageResponse, dependencies=[Depends(admin_only)])
async def enroll_students(data: EnrollmentCreate, db: AsyncSession = Depends(get_db)):
    await course_service.enroll_students(data.course_id, data.academic_session_id, data.student_ids, db)
    return MessageResponse(message=f"Enrolled {len(data.student_ids)} students successfully")

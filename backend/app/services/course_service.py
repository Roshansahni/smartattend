"""Course and enrollment service."""
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.models.course import Course, AcademicSession
from app.models.enrollment import Enrollment, CourseFacultyAssignment
from app.schemas.course import CourseCreate

async def create_course(data: CourseCreate, db: AsyncSession) -> Course:
    course = Course(
        id=uuid.uuid4(),
        code=data.code.upper(),
        name=data.name,
        description=data.description,
        department_id=data.department_id,
        credit_hours=data.credit_hours,
        semester=data.semester,
        is_active=True
    )
    db.add(course)
    await db.flush()
    return course

async def list_courses(db: AsyncSession):
    stmt = select(Course).options(joinedload(Course.department))
    res = await db.execute(stmt)
    return res.scalars().all()

async def enroll_students(course_id: uuid.UUID, session_id: uuid.UUID, student_ids: List[uuid.UUID], db: AsyncSession):
    for sid in student_ids:
        exists = await db.execute(
            select(Enrollment).where(
                Enrollment.student_id == sid,
                Enrollment.course_id == course_id,
                Enrollment.academic_session_id == session_id
            )
        )
        if not exists.scalar_one_or_none():
            db.add(Enrollment(
                id=uuid.uuid4(),
                student_id=sid,
                course_id=course_id,
                academic_session_id=session_id,
                is_active=True
            ))
    await db.flush()

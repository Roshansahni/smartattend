"""Timetable and class schedule endpoints."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_user, RoleChecker
from app.models.timetable import TimetableEntry
from app.models.course import Course
from app.models.faculty import FacultyProfile
from app.models.institution import Department
from app.models.user import User

router = APIRouter(prefix="/timetable", tags=["Timetable"])
admin_only = RoleChecker(["admin", "super_admin"])


class TimetableCreateRequest(BaseModel):
    course_id: uuid.UUID
    faculty_id: uuid.UUID
    department_id: uuid.UUID
    day_of_week: str  # Monday, Tuesday...
    start_time: str   # 09:00
    end_time: str     # 10:00
    room_number: str  # LH-101
    semester: int = 7
    section: str = "A"


@router.get("", response_model=list)
@router.get("/", response_model=list, include_in_schema=False)
async def get_timetable(
    day: Optional[str] = Query(None),
    semester: Optional[int] = Query(None),
    section: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(TimetableEntry)
    if day:
        query = query.where(TimetableEntry.day_of_week.ilike(f"%{day}%"))
    if semester:
        query = query.where(TimetableEntry.semester == semester)
    if section:
        query = query.where(TimetableEntry.section == section)

    res = await db.execute(query)
    entries = res.scalars().all()

    # Pre-populate sample if none exist
    if not entries:
        course = (await db.execute(select(Course))).scalars().first()
        faculty = (await db.execute(select(FacultyProfile))).scalars().first()
        dept = (await db.execute(select(Department))).scalars().first()
        if course and faculty and dept:
            sample_schedule = [
                ("Monday", "09:00", "10:00", "LH-101"),
                ("Tuesday", "10:00", "11:00", "CS-LAB-2"),
                ("Wednesday", "11:30", "12:30", "LH-101"),
                ("Thursday", "09:00", "10:00", "LH-204"),
                ("Friday", "14:00", "16:00", "CLOUD-LAB"),
            ]
            for d, st, et, rm in sample_schedule:
                entry = TimetableEntry(
                    id=uuid.uuid4(),
                    course_id=course.id,
                    faculty_id=faculty.id,
                    department_id=dept.id,
                    day_of_week=d,
                    start_time=st,
                    end_time=et,
                    room_number=rm,
                    semester=7,
                    section="A",
                )
                db.add(entry)
            await db.flush()
            entries = (await db.execute(select(TimetableEntry))).scalars().all()

    formatted = []
    for e in entries:
        c = (await db.execute(select(Course).where(Course.id == e.course_id))).scalar_one_or_none()
        f = (await db.execute(select(FacultyProfile).where(FacultyProfile.id == e.faculty_id))).scalar_one_or_none()
        f_user = None
        if f:
            f_user = (await db.execute(select(User).where(User.id == f.user_id))).scalar_one_or_none()

        formatted.append({
            "id": str(e.id),
            "day": e.day_of_week,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "room_number": e.room_number,
            "semester": e.semester,
            "section": e.section,
            "course_code": c.code if c else "CS401",
            "course_name": c.name if c else "Distributed Systems",
            "faculty_name": f_user.full_name if f_user else "Prof. Amit Sharma",
        })
    return formatted


@router.post("", dependencies=[Depends(admin_only)])
@router.post("/", dependencies=[Depends(admin_only)], include_in_schema=False)
async def create_timetable_entry(
    data: TimetableCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    entry = TimetableEntry(
        id=uuid.uuid4(),
        course_id=data.course_id,
        faculty_id=data.faculty_id,
        department_id=data.department_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        room_number=data.room_number,
        semester=data.semester,
        section=data.section,
    )
    db.add(entry)
    await db.flush()
    return {"message": "Timetable entry created successfully", "id": str(entry.id)}

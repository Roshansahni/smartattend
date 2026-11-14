"""Attendance analytics business logic."""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.student import Student
from app.models.faculty import FacultyProfile
from app.models.course import Course
from app.models.attendance import AttendanceSession, AttendanceRecord

async def get_admin_dashboard_stats(db: AsyncSession) -> dict:
    total_students = (await db.execute(select(func.count(Student.id)))).scalar_one()
    total_faculty = (await db.execute(select(func.count(FacultyProfile.id)))).scalar_one()
    total_courses = (await db.execute(select(func.count(Course.id)))).scalar_one()
    active_sessions = (await db.execute(select(func.count(AttendanceSession.id)).where(AttendanceSession.is_active == True))).scalar_one()
    
    total_records = (await db.execute(select(func.count(AttendanceRecord.id)))).scalar_one()
    present_records = (await db.execute(select(func.count(AttendanceRecord.id)).where(AttendanceRecord.is_present == True))).scalar_one()
    avg_att = (present_records / total_records * 100.0) if total_records > 0 else 0.0
    
    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_courses": total_courses,
        "total_sessions_today": active_sessions,
        "active_sessions_now": active_sessions,
        "average_attendance_percentage": round(avg_att, 1),
        "low_attendance_students": 0
    }

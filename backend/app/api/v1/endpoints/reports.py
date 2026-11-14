"""Reports and export endpoints."""
import uuid
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.student import Student
from app.utils.pdf_generator import generate_attendance_pdf
import io
import csv

router = APIRouter(prefix="/reports", tags=["Reports"])
staff_only = RoleChecker(["admin", "super_admin", "faculty"])

@router.get("/attendance/csv", dependencies=[Depends(staff_only)])
async def export_attendance_csv(session_id: uuid.UUID = Query(...), db: AsyncSession = Depends(get_db)):
    stmt = select(AttendanceRecord).where(AttendanceRecord.attendance_session_id == session_id).options(
        joinedload(AttendanceRecord.student).joinedload(Student.user)
    )
    records = (await db.execute(stmt)).scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Enrollment Number", "Student Name", "Status", "Marked At", "Method"])
    for r in records:
        writer.writerow([
            r.student.enrollment_number if r.student else "",
            r.student.user.full_name if r.student and r.student.user else "",
            "Present" if r.is_present else "Absent",
            r.marked_at.isoformat(),
            r.verification_method
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_{session_id}.csv"}
    )

@router.get("/attendance/pdf", dependencies=[Depends(staff_only)])
async def export_attendance_pdf(session_id: uuid.UUID = Query(...), db: AsyncSession = Depends(get_db)):
    sess = (await db.execute(select(AttendanceSession).where(AttendanceSession.id == session_id))).scalar_one_or_none()
    stmt = select(AttendanceRecord).where(AttendanceRecord.attendance_session_id == session_id).options(
        joinedload(AttendanceRecord.student).joinedload(Student.user)
    )
    records = (await db.execute(stmt)).scalars().all()
    data = {
        "title": sess.title if sess else "Attendance",
        "records": [
            {
                "enrollment_number": r.student.enrollment_number if r.student else "",
                "student_name": r.student.user.full_name if r.student and r.student.user else "",
                "is_present": r.is_present,
                "marked_at": r.marked_at,
                "verification_method": r.verification_method
            }
            for r in records
        ]
    }
    pdf_bytes = generate_attendance_pdf(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=attendance_{session_id}.pdf"}
    )

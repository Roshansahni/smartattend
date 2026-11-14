"""Attendance disputes and correction requests."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_user, RoleChecker
from app.models.dispute import AttendanceDispute, DisputeStatus
from app.models.student import Student
from app.models.course import Course
from app.models.user import User

router = APIRouter(prefix="/disputes", tags=["Attendance Disputes"])
faculty_or_admin = RoleChecker(["faculty", "admin", "super_admin"])


class DisputeCreateRequest(BaseModel):
    course_id: uuid.UUID
    session_date: str
    reason: str


class DisputeResolveRequest(BaseModel):
    status: str  # resolved or rejected
    response: Optional[str] = None


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_dispute(
    data: DisputeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = (await db.execute(select(Student).where(Student.user_id == current_user.id))).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    dispute = AttendanceDispute(
        id=uuid.uuid4(),
        student_id=student.id,
        course_id=data.course_id,
        session_date=data.session_date,
        reason=data.reason,
        status=DisputeStatus.PENDING,
    )
    db.add(dispute)
    await db.flush()
    return {"message": "Attendance correction request submitted to instructor", "id": str(dispute.id)}


@router.get("/my-disputes")
async def get_my_disputes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = (await db.execute(select(Student).where(Student.user_id == current_user.id))).scalar_one_or_none()
    if not student:
        return []

    res = await db.execute(select(AttendanceDispute).where(AttendanceDispute.student_id == student.id).order_by(AttendanceDispute.created_at.desc()))
    disputes = res.scalars().all()
    results = []
    for d in disputes:
        c = (await db.execute(select(Course).where(Course.id == d.course_id))).scalar_one_or_none()
        results.append({
            "id": str(d.id),
            "course_code": c.code if c else "CS401",
            "course_name": c.name if c else "Distributed Systems",
            "session_date": d.session_date,
            "reason": d.reason,
            "status": str(d.status),
            "faculty_response": d.faculty_response,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        })
    return results


@router.get("/pending", dependencies=[Depends(faculty_or_admin)])
async def get_pending_disputes(
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(AttendanceDispute).order_by(AttendanceDispute.created_at.desc()))
    disputes = res.scalars().all()
    results = []
    for d in disputes:
        c = (await db.execute(select(Course).where(Course.id == d.course_id))).scalar_one_or_none()
        stu = (await db.execute(select(Student).where(Student.id == d.student_id))).scalar_one_or_none()
        u = None
        if stu:
            u = (await db.execute(select(User).where(User.id == stu.user_id))).scalar_one_or_none()
        results.append({
            "id": str(d.id),
            "student_name": u.full_name if u else "Student",
            "enrollment_number": stu.enrollment_number if stu else "N/A",
            "course_code": c.code if c else "CS401",
            "session_date": d.session_date,
            "reason": d.reason,
            "status": str(d.status),
            "faculty_response": d.faculty_response,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        })
    return results


@router.put("/{dispute_id}/resolve", dependencies=[Depends(faculty_or_admin)])
async def resolve_dispute(
    dispute_id: uuid.UUID,
    data: DisputeResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    dispute = (await db.execute(select(AttendanceDispute).where(AttendanceDispute.id == dispute_id))).scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute request not found")

    new_status = data.status.lower()
    dispute.status = DisputeStatus.RESOLVED if new_status == "resolved" else DisputeStatus.REJECTED
    dispute.faculty_response = data.response
    dispute.resolved_at = datetime.now(tz=timezone.utc)
    db.add(dispute)
    await db.flush()
    return {"message": f"Dispute marked as {new_status}"}

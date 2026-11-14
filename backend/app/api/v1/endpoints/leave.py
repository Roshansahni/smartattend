"""Leave application and approval endpoints."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_user, RoleChecker
from app.models.leave import LeaveApplication, LeaveType, LeaveStatus
from app.models.student import Student
from app.models.faculty import FacultyProfile
from app.models.user import User

router = APIRouter(prefix="/leave", tags=["Leave Management"])
student_only = RoleChecker(["student"])
faculty_or_admin = RoleChecker(["faculty", "admin", "super_admin"])
admin_only = RoleChecker(["admin", "super_admin"])


class LeaveApplyRequest(BaseModel):
    leave_type: str = "casual"
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    reason: str


class LeaveReviewRequest(BaseModel):
    status: str      # approved or rejected
    remarks: Optional[str] = None


@router.post("/apply", status_code=status.HTTP_201_CREATED)
async def apply_leave(
    data: LeaveApplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = (await db.execute(select(Student).where(Student.user_id == current_user.id))).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    from datetime import date
    try:
        s_date = date.fromisoformat(data.start_date)
        e_date = date.fromisoformat(data.end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    app = LeaveApplication(
        id=uuid.uuid4(),
        student_id=student.id,
        leave_type=data.leave_type.lower(),
        start_date=s_date,
        end_date=e_date,
        reason=data.reason,
        status=LeaveStatus.PENDING,
    )
    db.add(app)
    await db.flush()
    return {"message": "Leave application submitted successfully", "id": str(app.id)}


@router.get("/my-applications")
async def get_my_leave_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = (await db.execute(select(Student).where(Student.user_id == current_user.id))).scalar_one_or_none()
    if not student:
        return []

    res = await db.execute(
        select(LeaveApplication).where(LeaveApplication.student_id == student.id).order_by(LeaveApplication.applied_at.desc())
    )
    apps = res.scalars().all()
    return [
        {
            "id": str(a.id),
            "leave_type": str(a.leave_type).upper(),
            "start_date": str(a.start_date),
            "end_date": str(a.end_date),
            "reason": a.reason,
            "status": str(a.status),
            "faculty_remarks": a.faculty_remarks,
            "applied_at": a.applied_at.isoformat() if a.applied_at else None,
        }
        for a in apps
    ]


@router.get("/pending-reviews", dependencies=[Depends(faculty_or_admin)])
async def get_pending_leaves(
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(LeaveApplication).order_by(LeaveApplication.applied_at.desc())
    )
    apps = res.scalars().all()
    results = []
    for a in apps:
        stu = (await db.execute(select(Student).where(Student.id == a.student_id))).scalar_one_or_none()
        user_info = None
        if stu:
            u = (await db.execute(select(User).where(User.id == stu.user_id))).scalar_one_or_none()
            if u:
                user_info = {"name": u.full_name, "enrollment": stu.enrollment_number}

        results.append({
            "id": str(a.id),
            "student_name": user_info["name"] if user_info else "Student",
            "enrollment_number": user_info["enrollment"] if user_info else "N/A",
            "leave_type": str(a.leave_type).upper(),
            "start_date": str(a.start_date),
            "end_date": str(a.end_date),
            "reason": a.reason,
            "status": str(a.status),
            "faculty_remarks": a.faculty_remarks,
            "applied_at": a.applied_at.isoformat() if a.applied_at else None,
        })
    return results


@router.put("/{application_id}/review", dependencies=[Depends(faculty_or_admin)])
async def review_leave_application(
    application_id: uuid.UUID,
    data: LeaveReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = (await db.execute(select(LeaveApplication).where(LeaveApplication.id == application_id))).scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Leave application not found")

    new_status = data.status.lower()
    if new_status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be approved or rejected")

    fac = (await db.execute(select(FacultyProfile).where(FacultyProfile.user_id == current_user.id))).scalar_one_or_none()
    app.status = LeaveStatus.APPROVED if new_status == "approved" else LeaveStatus.REJECTED
    app.faculty_remarks = data.remarks
    app.reviewed_by_id = fac.id if fac else None
    app.reviewed_at = datetime.now(tz=timezone.utc)
    db.add(app)
    await db.flush()
    return {"message": f"Leave application {new_status} successfully"}

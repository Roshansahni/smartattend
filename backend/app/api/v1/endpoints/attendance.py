"""Attendance management endpoints."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.core.dependencies import get_current_user, RoleChecker, get_client_ip
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.schemas.attendance import (
    AttendanceSessionCreate, AttendanceSessionResponse, QRTokenResponse,
    AttendanceMarkRequest, AttendanceRecordResponse, AttendanceEditRequest,
    LiveAttendanceRecord
)
from app.schemas.common import MessageResponse
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["Attendance"])

faculty_or_admin = RoleChecker(["faculty", "admin", "super_admin"])

@router.post("/sessions", response_model=AttendanceSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: AttendanceSessionCreate,
    current_user=Depends(faculty_or_admin),
    db: AsyncSession = Depends(get_db),
):
    session = await attendance_service.create_attendance_session(
        course_id=data.course_id,
        faculty_user_id=current_user.id,
        academic_session_id=data.academic_session_id,
        title=data.title,
        gps_required=data.gps_required,
        location_lat=data.location_lat,
        location_lng=data.location_lng,
        location_radius_meters=data.location_radius_meters,
        db=db,
    )
    return AttendanceSessionResponse.model_validate(session)

@router.post("/sessions/{session_id}/start", response_model=AttendanceSessionResponse)
async def start_session(
    session_id: uuid.UUID,
    current_user=Depends(faculty_or_admin),
    db: AsyncSession = Depends(get_db),
):
    session = await attendance_service.start_session(session_id, current_user.id, db)
    return AttendanceSessionResponse.model_validate(session)

@router.post("/sessions/{session_id}/end", response_model=AttendanceSessionResponse)
async def end_session(
    session_id: uuid.UUID,
    current_user=Depends(faculty_or_admin),
    db: AsyncSession = Depends(get_db),
):
    session = await attendance_service.end_session(session_id, current_user.id, db)
    return AttendanceSessionResponse.model_validate(session)

@router.get("/sessions/{session_id}/qr", response_model=QRTokenResponse)
async def get_qr_code(
    session_id: uuid.UUID,
    current_user=Depends(faculty_or_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await attendance_service.generate_qr_for_session(
        session_id=session_id,
        faculty_user_id=current_user.id,
        db=db,
    )
    return QRTokenResponse(**result)

@router.post("/sessions/{session_id}/qr/rotate", response_model=QRTokenResponse)
async def rotate_qr(
    session_id: uuid.UUID,
    current_user=Depends(faculty_or_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await attendance_service.generate_qr_for_session(
        session_id=session_id,
        faculty_user_id=current_user.id,
        db=db,
    )
    return QRTokenResponse(**result)

@router.post("/mark", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    request_data: AttendanceMarkRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.primary_role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can mark attendance via QR scan"
        )

    ip = get_client_ip(request)
    await attendance_service.mark_attendance(
        student_user_id=current_user.id,
        request=request_data,
        ip_address=ip,
        db=db,
    )
    return MessageResponse(message="Attendance marked successfully! ✓")

@router.get("/sessions/{session_id}/records", response_model=list[LiveAttendanceRecord])
async def get_session_records(
    session_id: uuid.UUID,
    current_user=Depends(faculty_or_admin),
    db: AsyncSession = Depends(get_db),
):
    records = await attendance_service.get_session_live_attendance(session_id, db)
    return records

@router.put("/records/{record_id}", response_model=MessageResponse)
async def edit_record(
    record_id: uuid.UUID,
    edit_data: AttendanceEditRequest,
    current_user=Depends(faculty_or_admin),
    db: AsyncSession = Depends(get_db),
):
    await attendance_service.edit_attendance_record(
        record_id=record_id,
        is_present=edit_data.is_present,
        edit_reason=edit_data.edit_reason,
        editor_user_id=current_user.id,
        db=db,
    )
    return MessageResponse(message="Attendance record updated with audit log")

@router.get("/my-attendance")
async def get_my_attendance(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.primary_role != "student":
        raise HTTPException(status_code=403, detail="Students only")

    from app.models.student import Student
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        return []

    result = await db.execute(
        select(AttendanceRecord)
        .where(AttendanceRecord.student_id == student.id)
        .order_by(AttendanceRecord.marked_at.desc())
    )
    records = result.scalars().all()
    return [AttendanceRecordResponse.model_validate(r) for r in records]

"""
Attendance Service — The Core of SmartAttend

Security-first implementation:
1. Student identity from JWT ONLY (never request body)
2. QR token validated server-side (exists, not expired, session active)
3. Enrollment checked before allowing mark
4. Duplicate prevention at app level + DB UNIQUE constraint
5. GPS distance validated server-side if required
6. All timestamps from server (never client-submitted)
7. Audit log for every edit
"""
import uuid
import base64
import io
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError

from app.models.attendance import AttendanceSession, QRToken, AttendanceRecord, VerificationMethod
from app.models.enrollment import Enrollment
from app.models.faculty import FacultyProfile
from app.models.student import Student
from app.models.audit import AuditLog
from app.core.security import generate_qr_token
from app.core.config import get_settings
from app.core.exceptions import (
    NotFoundException, QRExpiredException, QRInvalidException,
    DuplicateAttendanceException, SessionInactiveException,
    NotEnrolledException, GPSVerificationFailedException, ForbiddenException
)
from app.schemas.attendance import AttendanceSessionCreate, AttendanceMarkRequest
from app.utils.qr_generator import generate_qr_image
from app.utils.gps import calculate_distance

settings = get_settings()


async def create_attendance_session(
    course_id: uuid.UUID,
    faculty_user_id: uuid.UUID,
    academic_session_id: uuid.UUID,
    title: str,
    gps_required: bool,
    location_lat: Optional[float],
    location_lng: Optional[float],
    location_radius_meters: int,
    db: AsyncSession,
) -> AttendanceSession:
    """Create a new attendance session for a course."""
    # Get faculty profile from user ID
    result = await db.execute(
        select(FacultyProfile).where(FacultyProfile.user_id == faculty_user_id)
    )
    faculty = result.scalar_one_or_none()
    if not faculty:
        raise NotFoundException("Faculty profile")

    if gps_required and (location_lat is None or location_lng is None):
        from app.core.exceptions import ValidationException
        raise ValidationException("GPS coordinates required when GPS verification is enabled")

    session = AttendanceSession(
        id=uuid.uuid4(),
        course_id=course_id,
        faculty_id=faculty.id,
        academic_session_id=academic_session_id,
        title=title,
        is_active=False,
        gps_required=gps_required,
        location_lat=location_lat,
        location_lng=location_lng,
        location_radius_meters=location_radius_meters,
    )
    db.add(session)
    await db.flush()
    return session


async def start_session(session_id: uuid.UUID, faculty_user_id: uuid.UUID, db: AsyncSession) -> AttendanceSession:
    """Start an attendance session and generate the first QR token."""
    result = await db.execute(select(AttendanceSession).where(AttendanceSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Attendance session")

    # Verify faculty owns this session
    faculty_result = await db.execute(
        select(FacultyProfile).where(FacultyProfile.user_id == faculty_user_id)
    )
    faculty = faculty_result.scalar_one_or_none()
    if not faculty or session.faculty_id != faculty.id:
        raise ForbiddenException("You can only manage your own sessions")

    session.is_active = True
    session.started_at = datetime.now(tz=timezone.utc)
    db.add(session)
    await db.flush()
    return session


async def end_session(session_id: uuid.UUID, faculty_user_id: uuid.UUID, db: AsyncSession) -> AttendanceSession:
    """End an attendance session."""
    result = await db.execute(select(AttendanceSession).where(AttendanceSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Attendance session")

    faculty_result = await db.execute(
        select(FacultyProfile).where(FacultyProfile.user_id == faculty_user_id)
    )
    faculty = faculty_result.scalar_one_or_none()
    if not faculty or session.faculty_id != faculty.id:
        raise ForbiddenException("You can only manage your own sessions")

    session.is_active = False
    session.ended_at = datetime.now(tz=timezone.utc)
    db.add(session)
    return session


async def generate_qr_for_session(
    session_id: uuid.UUID,
    faculty_user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    """
    Generate (or regenerate) a QR token for an active session.
    Called when session starts and periodically by auto-rotation.

    Returns dict with:
    - qr_image_base64: PNG image as data URI
    - token_expires_at: When this QR expires
    - refresh_interval_seconds: When frontend should request new QR
    """
    result = await db.execute(select(AttendanceSession).where(AttendanceSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundException("Attendance session")

    if not session.is_active:
        raise SessionInactiveException()

    # Verify faculty ownership
    faculty_result = await db.execute(
        select(FacultyProfile).where(FacultyProfile.user_id == faculty_user_id)
    )
    faculty = faculty_result.scalar_one_or_none()
    if not faculty or session.faculty_id != faculty.id:
        raise ForbiddenException("Access denied")

    # Generate secure token
    token_value = generate_qr_token()
    expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=settings.qr_token_expire_seconds)

    qr_token = QRToken(
        id=uuid.uuid4(),
        session_id=session_id,
        token=token_value,
        expires_at=expires_at,
        is_used=False,
    )
    db.add(qr_token)
    await db.flush()

    # Generate QR image
    qr_image_base64 = generate_qr_image(token_value)

    return {
        "session_id": session_id,
        "qr_image_base64": qr_image_base64,
        "token_expires_at": expires_at,
        "refresh_interval_seconds": settings.qr_refresh_interval_seconds,
    }


async def mark_attendance(
    student_user_id: uuid.UUID,
    request: AttendanceMarkRequest,
    ip_address: Optional[str],
    db: AsyncSession,
) -> AttendanceRecord:
    """
    Mark attendance for a student using a QR token.

    Security checks (in order):
    1. Validate QR token exists
    2. Validate token not expired (server time)
    3. Validate session is active
    4. Validate student is enrolled in the course
    5. Check no duplicate attendance record
    6. GPS validation if required
    7. Insert attendance record (DB UNIQUE constraint is final guard)
    """
    # Step 1: Get student profile from JWT user_id
    student_result = await db.execute(
        select(Student).where(Student.user_id == student_user_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise NotFoundException("Student profile")

    # Step 2: Look up QR token
    token_result = await db.execute(
        select(QRToken).where(QRToken.token == request.qr_token)
    )
    qr_token = token_result.scalar_one_or_none()

    if qr_token is None:
        raise QRInvalidException()

    # Step 3: Check expiry (server time)
    now_utc = datetime.now(tz=timezone.utc)
    token_expires = qr_token.expires_at
    if token_expires.tzinfo is None:
        token_expires = token_expires.replace(tzinfo=timezone.utc)
    if now_utc > token_expires:
        raise QRExpiredException()

    # Step 4: Get the attendance session
    session_result = await db.execute(
        select(AttendanceSession).where(AttendanceSession.id == qr_token.session_id)
    )
    att_session = session_result.scalar_one_or_none()
    if not att_session:
        raise QRInvalidException()

    # Step 5: Check session is active
    if not att_session.is_active:
        raise SessionInactiveException()

    # Step 6: Check enrollment
    enrollment_result = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student.id,
            Enrollment.course_id == att_session.course_id,
            Enrollment.academic_session_id == att_session.academic_session_id,
            Enrollment.is_active == True,
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    if not enrollment:
        raise NotEnrolledException()

    # Step 7: Check for duplicate (pre-check before DB insert)
    duplicate_result = await db.execute(
        select(AttendanceRecord).where(
            AttendanceRecord.attendance_session_id == att_session.id,
            AttendanceRecord.student_id == student.id,
        )
    )
    if duplicate_result.scalar_one_or_none():
        raise DuplicateAttendanceException()

    # Step 8: GPS verification (if required by faculty)
    distance_meters = None
    if att_session.gps_required:
        if request.lat is None or request.lng is None:
            from app.core.exceptions import ValidationException
            raise ValidationException("GPS location is required for this session. Please allow location access.")

        distance_meters = calculate_distance(
            att_session.location_lat, att_session.location_lng,
            request.lat, request.lng
        )
        if distance_meters > att_session.location_radius_meters:
            raise GPSVerificationFailedException(distance_meters, att_session.location_radius_meters)

    # Step 9: Insert attendance record
    # DB UNIQUE constraint (session_id, student_id) is the final guard against race conditions
    record = AttendanceRecord(
        id=uuid.uuid4(),
        attendance_session_id=att_session.id,
        student_id=student.id,
        qr_token_id=qr_token.id,
        marked_at=datetime.now(tz=timezone.utc),  # Server timestamp
        is_present=True,
        verification_method=VerificationMethod.QR,
        student_lat=request.lat,
        student_lng=request.lng,
        distance_meters=distance_meters,
        ip_address=ip_address,
        is_edited=False,
    )
    db.add(record)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise DuplicateAttendanceException()

    return record


async def edit_attendance_record(
    record_id: uuid.UUID,
    is_present: bool,
    edit_reason: str,
    editor_user_id: uuid.UUID,
    db: AsyncSession,
) -> AttendanceRecord:
    """
    Faculty edits an attendance record.
    Creates an audit log entry for transparency.
    """
    result = await db.execute(select(AttendanceRecord).where(AttendanceRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise NotFoundException("Attendance record")

    # Save old value for audit
    old_value = {"is_present": record.is_present, "is_edited": record.is_edited}

    # Update
    record.is_present = is_present
    record.is_edited = True
    record.edit_reason = edit_reason
    record.edited_by = editor_user_id
    db.add(record)

    # Create audit log
    audit = AuditLog(
        id=uuid.uuid4(),
        user_id=editor_user_id,
        action="EDIT_ATTENDANCE",
        resource_type="attendance_record",
        resource_id=str(record_id),
        old_value=old_value,
        new_value={"is_present": is_present, "edit_reason": edit_reason},
    )
    db.add(audit)
    await db.flush()
    return record


async def get_session_live_attendance(session_id: uuid.UUID, db: AsyncSession) -> list:
    """Get real-time attendance list for faculty dashboard."""
    from app.models.user import User
    from sqlalchemy.orm import joinedload

    result = await db.execute(
        select(AttendanceRecord)
        .where(AttendanceRecord.attendance_session_id == session_id)
        .options(joinedload(AttendanceRecord.student).joinedload(Student.user))
        .order_by(AttendanceRecord.marked_at.asc())
    )
    records = result.scalars().all()

    return [
        {
            "record_id": r.id,
            "student_id": r.student_id,
            "student_name": r.student.user.full_name if r.student and r.student.user else "Unknown",
            "enrollment_number": r.student.enrollment_number if r.student else "N/A",
            "marked_at": r.marked_at,
            "verification_method": r.verification_method,
            "is_edited": r.is_edited,
        }
        for r in records
    ]

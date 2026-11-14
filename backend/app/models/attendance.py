"""
Attendance models — the core of SmartAttend.

Security design:
1. AttendanceSession: Faculty creates this to start taking attendance
2. QRToken: Short-lived (30s), cryptographically random, single-session use
3. AttendanceRecord: One per student per session (enforced by UNIQUE constraint)

The UNIQUE constraint on attendance_records(session_id, student_id) is the
last line of defense against duplicate attendance — even if the application
layer fails, the DB will reject duplicates.
"""
import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import (
    String, Boolean, Float, DateTime, ForeignKey,
    UniqueConstraint, Index, Enum as SAEnum, func, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.base import Base, TimestampMixin


class VerificationMethod(str, enum.Enum):
    QR = "qr"
    MANUAL = "manual"
    GPS = "gps"


class AttendanceSession(Base, TimestampMixin):
    """
    An attendance-taking session created by faculty for a specific course.
    Faculty starts the session → generates QR → students scan → session ends.
    """
    __tablename__ = "attendance_sessions"
    __table_args__ = (
        Index("ix_att_session_course_active", "course_id", "is_active"),
        Index("ix_att_session_faculty", "faculty_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    faculty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("faculty_profiles.id", ondelete="RESTRICT"), nullable=False
    )
    academic_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_sessions.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="Attendance Session")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # GPS verification fields
    location_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_radius_meters: Mapped[int] = mapped_column(nullable=False, default=100)
    gps_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="attendance_sessions")
    faculty: Mapped["FacultyProfile"] = relationship("FacultyProfile", back_populates="attendance_sessions")
    academic_session: Mapped["AcademicSession"] = relationship("AcademicSession", back_populates="attendance_sessions")
    qr_tokens: Mapped[list["QRToken"]] = relationship("QRToken", back_populates="session")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="session")

    def __repr__(self) -> str:
        return f"<AttendanceSession {self.id} course={self.course_id} active={self.is_active}>"


class QRToken(Base):
    """
    Short-lived QR token for secure attendance marking.

    Security properties:
    - token: 32 bytes of cryptographically random data (secrets.token_urlsafe)
    - expires_at: Set by backend, 30 seconds from creation
    - is_used: Once a student uses it, optionally mark used (for extra replay protection)

    Note: We allow the token to be scanned by MULTIPLE students in the 30s window
    (since multiple students need to scan the SAME displayed QR). The duplicate
    attendance protection is at the attendance_records level (UNIQUE constraint).
    """
    __tablename__ = "qr_tokens"
    __table_args__ = (
        Index("ix_qr_token_session_active", "session_id", "is_used"),
        Index("ix_qr_token_expires", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session: Mapped["AttendanceSession"] = relationship("AttendanceSession", back_populates="qr_tokens")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="qr_token")

    @property
    def is_expired(self) -> bool:
        """Check if token has expired (using Python datetime comparison)."""
        from datetime import timezone
        return datetime.now(tz=timezone.utc) > self.expires_at.replace(tzinfo=timezone.utc) if self.expires_at.tzinfo is None else datetime.now(tz=timezone.utc) > self.expires_at

    def __repr__(self) -> str:
        return f"<QRToken {self.token[:8]}... expires={self.expires_at}>"


class AttendanceRecord(Base):
    """
    Single attendance record for one student in one session.

    Critical security: UNIQUE constraint on (attendance_session_id, student_id)
    ensures absolute duplicate prevention at the database level.

    Fields:
    - student_id: Extracted from JWT (never from request body)
    - qr_token_id: Which QR they used (for audit trail)
    - marked_at: Server timestamp (never client-provided)
    - is_edited: Tracks if faculty manually edited this record
    - edit_reason: Mandatory when editing (audit trail)
    """
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("attendance_session_id", "student_id", name="uq_attendance_record"),
        Index("ix_att_record_student", "student_id"),
        Index("ix_att_record_session", "attendance_session_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attendance_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("attendance_sessions.id", ondelete="RESTRICT"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="RESTRICT"), nullable=False
    )
    qr_token_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qr_tokens.id", ondelete="SET NULL"), nullable=True
    )
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_present: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verification_method: Mapped[str] = mapped_column(
        SAEnum(VerificationMethod, name="verification_method_enum"), nullable=False, default=VerificationMethod.QR
    )

    # GPS data (optional)
    student_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    student_lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Edit tracking (audit trail)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    edit_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    edited_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session: Mapped["AttendanceSession"] = relationship("AttendanceSession", back_populates="attendance_records")
    student: Mapped["Student"] = relationship("Student", back_populates="attendance_records")
    qr_token: Mapped[Optional["QRToken"]] = relationship("QRToken", back_populates="attendance_records")

    def __repr__(self) -> str:
        return f"<AttendanceRecord student={self.student_id} session={self.attendance_session_id} present={self.is_present}>"

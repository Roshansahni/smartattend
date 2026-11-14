"""Attendance dispute and correction request model."""
import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import UUID, Base


class DisputeStatus(str, enum.Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class AttendanceDispute(Base):
    """Student attendance correction request."""
    __tablename__ = "attendance_disputes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    session_date: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(DisputeStatus, name="dispute_status_enum"), nullable=False, default=DisputeStatus.PENDING, index=True
    )
    faculty_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship("Student")
    course: Mapped["Course"] = relationship("Course")

"""Leave Application model for student online leave requests."""
import uuid
import enum
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Text, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import UUID, Base


class LeaveType(str, enum.Enum):
    MEDICAL = "medical"
    CASUAL = "casual"
    ACADEMIC = "academic"
    DUTY = "duty"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LeaveApplication(Base):
    """Student leave application submitted to faculty/HOD."""
    __tablename__ = "leave_applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    leave_type: Mapped[str] = mapped_column(
        SAEnum(LeaveType, name="leave_type_enum"), nullable=False, default=LeaveType.CASUAL
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(LeaveStatus, name="leave_status_enum"), nullable=False, default=LeaveStatus.PENDING, index=True
    )
    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("faculty_profiles.id", ondelete="SET NULL"), nullable=True
    )
    faculty_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship("Student")
    reviewed_by: Mapped[Optional["FacultyProfile"]] = relationship("FacultyProfile")

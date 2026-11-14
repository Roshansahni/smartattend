"""Faculty profile model."""
import uuid
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import UUID
from app.db.base import Base, TimestampMixin


class FacultyProfile(Base, TimestampMixin):
    """
    Faculty-specific profile data.
    Linked 1-to-1 with the User model.
    Contains institutional information like employee ID, department, designation.
    """
    __tablename__ = "faculty_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False
    )
    designation: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Assistant Professor"
    specialization: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    joined_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="faculty_profile")
    department: Mapped["Department"] = relationship(
        "Department", back_populates="faculty_members",
        primaryjoin="FacultyProfile.department_id == Department.id",
        foreign_keys=[department_id],
    )
    course_assignments: Mapped[List["CourseFacultyAssignment"]] = relationship(
        "CourseFacultyAssignment", back_populates="faculty"
    )
    attendance_sessions: Mapped[List["AttendanceSession"]] = relationship(
        "AttendanceSession", back_populates="faculty"
    )

    def __repr__(self) -> str:
        return f"<Faculty {self.employee_id}>"

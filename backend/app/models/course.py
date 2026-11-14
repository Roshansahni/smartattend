"""Course and AcademicSession models."""
import uuid
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Boolean, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class AcademicSession(Base, TimestampMixin):
    """
    Represents a semester/academic session.
    Example: "2024-25 Even Semester" (Jan-May 2025)
    All courses, enrollments, and attendance are scoped to a session.
    """
    __tablename__ = "academic_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    enrollments: Mapped[List["Enrollment"]] = relationship("Enrollment", back_populates="academic_session")
    course_assignments: Mapped[List["CourseFacultyAssignment"]] = relationship(
        "CourseFacultyAssignment", back_populates="academic_session"
    )
    attendance_sessions: Mapped[List["AttendanceSession"]] = relationship(
        "AttendanceSession", back_populates="academic_session"
    )

    def __repr__(self) -> str:
        return f"<AcademicSession {self.name}>"


class Course(Base, TimestampMixin):
    """
    Represents a subject/course offered by a department.
    Example: CS601 - Machine Learning (CSE, Semester 6, 4 credits)
    """
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False
    )
    credit_hours: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)  # Which semester this is taught
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="courses")
    enrollments: Mapped[List["Enrollment"]] = relationship("Enrollment", back_populates="course")
    faculty_assignments: Mapped[List["CourseFacultyAssignment"]] = relationship(
        "CourseFacultyAssignment", back_populates="course"
    )
    attendance_sessions: Mapped[List["AttendanceSession"]] = relationship(
        "AttendanceSession", back_populates="course"
    )

    def __repr__(self) -> str:
        return f"<Course {self.code}: {self.name}>"

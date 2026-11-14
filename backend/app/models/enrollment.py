"""Enrollment and CourseFacultyAssignment models."""
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Boolean, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Enrollment(Base):
    """
    Student-Course enrollment for a specific academic session.

    Design: Unique constraint (student, course, session) prevents double enrollment.
    Soft-delete via is_active flag instead of hard delete.
    """
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", "academic_session_id", name="uq_enrollment"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    academic_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_sessions.id", ondelete="CASCADE"), nullable=False
    )
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")
    academic_session: Mapped["AcademicSession"] = relationship("AcademicSession", back_populates="enrollments")


class CourseFacultyAssignment(Base):
    """
    Assigns faculty to teach a course in a specific academic session.
    One course can have one primary faculty per session.
    """
    __tablename__ = "course_faculty_assignments"
    __table_args__ = (
        UniqueConstraint("faculty_id", "course_id", "academic_session_id", name="uq_cfa"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    academic_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_sessions.id", ondelete="CASCADE"), nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    faculty: Mapped["FacultyProfile"] = relationship("FacultyProfile", back_populates="course_assignments")
    course: Mapped["Course"] = relationship("Course", back_populates="faculty_assignments")
    academic_session: Mapped["AcademicSession"] = relationship("AcademicSession", back_populates="course_assignments")

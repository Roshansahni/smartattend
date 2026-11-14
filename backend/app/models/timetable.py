"""Timetable and Schedule models."""
import uuid
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import UUID, Base


class TimetableEntry(Base):
    """Weekly academic class schedule entry."""
    __tablename__ = "timetable_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    faculty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)  # Monday, Tuesday, etc.
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)   # "09:00"
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)     # "10:00"
    room_number: Mapped[str] = mapped_column(String(50), nullable=False)  # "LH-101"
    semester: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    section: Mapped[str] = mapped_column(String(10), nullable=False, default="A")

    # Relationships
    course: Mapped["Course"] = relationship("Course")
    faculty: Mapped["FacultyProfile"] = relationship("FacultyProfile")
    department: Mapped["Department"] = relationship("Department")

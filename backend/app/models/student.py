"""Student profile model."""
import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class Student(Base, TimestampMixin):
    """
    Student-specific profile data.
    Linked 1-to-1 with User model.

    Key fields:
    - enrollment_number: Unique identifier used in reports and QR verification
    - semester: Current semester (1-8 for 4-year B.Tech)
    - batch_year: Year of admission (used for cohort analytics)
    """
    __tablename__ = "students"
    __table_args__ = (
        Index("ix_students_dept_semester", "department_id", "semester"),
        Index("ix_students_batch", "batch_year"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    enrollment_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False
    )
    semester: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-8
    batch_year: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g. 2022
    section: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # e.g. "A", "B"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="student_profile")
    department: Mapped["Department"] = relationship("Department", back_populates="students")
    enrollments: Mapped[List["Enrollment"]] = relationship("Enrollment", back_populates="student")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="student")

    def __repr__(self) -> str:
        return f"<Student {self.enrollment_number}>"

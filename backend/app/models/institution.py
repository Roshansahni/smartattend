"""Department model for SmartAttend."""
import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class Department(Base, TimestampMixin):
    """
    Academic department within the institution.
    Example: Computer Science & Engineering (CSE)
    """
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    head_faculty_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("faculty_profiles.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    faculty_members: Mapped[List["FacultyProfile"]] = relationship(
        "FacultyProfile", back_populates="department",
        primaryjoin="Department.id == FacultyProfile.department_id",
        foreign_keys="FacultyProfile.department_id",
    )
    students: Mapped[List["Student"]] = relationship("Student", back_populates="department")
    courses: Mapped[List["Course"]] = relationship("Course", back_populates="department")

    def __repr__(self) -> str:
        return f"<Department {self.code}: {self.name}>"

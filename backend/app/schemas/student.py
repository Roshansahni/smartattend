"""Student Pydantic schemas."""
import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class StudentBase(BaseModel):
    enrollment_number: str
    semester: int
    batch_year: int
    section: Optional[str] = None

    @field_validator("semester")
    @classmethod
    def validate_semester(cls, v):
        if not 1 <= v <= 8:
            raise ValueError("Semester must be between 1 and 8")
        return v


class StudentCreate(StudentBase):
    # User fields
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    department_id: uuid.UUID


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    enrollment_number: str
    semester: int
    batch_year: int
    section: Optional[str]
    is_active: bool
    created_at: datetime
    # Nested
    user: "UserBasicInfo"
    department: "DepartmentBasicInfo"


class UserBasicInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    full_name: str
    phone: Optional[str]
    is_active: bool


class DepartmentBasicInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    code: str


class StudentAttendanceSummary(BaseModel):
    student_id: uuid.UUID
    student_name: str
    enrollment_number: str
    total_classes: int
    present_classes: int
    absent_classes: int
    attendance_percentage: float
    course_wise: list[dict]

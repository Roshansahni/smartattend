"""Course and enrollment schemas."""
import uuid
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    created_at: datetime


class AcademicSessionCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    is_current: bool = False


class AcademicSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    start_date: date
    end_date: date
    is_current: bool
    created_at: datetime


class CourseCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    department_id: uuid.UUID
    credit_hours: int = 3
    semester: int


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    credit_hours: Optional[int] = None
    is_active: Optional[bool] = None


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    code: str
    name: str
    description: Optional[str]
    credit_hours: int
    semester: int
    is_active: bool
    created_at: datetime
    department: "DepartmentBasicInfo"


class EnrollmentCreate(BaseModel):
    student_ids: list[uuid.UUID]
    course_id: uuid.UUID
    academic_session_id: uuid.UUID


class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    student_id: uuid.UUID
    course_id: uuid.UUID
    academic_session_id: uuid.UUID
    enrolled_at: datetime
    is_active: bool


from app.schemas.student import DepartmentBasicInfo  # noqa: E402
CourseResponse.model_rebuild()

"""Faculty Pydantic schemas."""
import uuid
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class FacultyBase(BaseModel):
    employee_id: str
    designation: str
    specialization: Optional[str] = None
    joined_date: Optional[date] = None


class FacultyCreate(FacultyBase):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    department_id: uuid.UUID


class FacultyUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    specialization: Optional[str] = None
    is_active: Optional[bool] = None


class FacultyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: str
    designation: str
    specialization: Optional[str]
    is_active: bool
    joined_date: Optional[date]
    created_at: datetime
    user: "UserBasicInfo"
    department: "DepartmentBasicInfo"


# Forward refs resolved by student.py's definitions — import there
from app.schemas.student import UserBasicInfo, DepartmentBasicInfo  # noqa: E402
FacultyResponse.model_rebuild()

"""Attendance-related Pydantic schemas."""
import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AttendanceSessionCreate(BaseModel):
    course_id: uuid.UUID
    academic_session_id: uuid.UUID
    title: str = "Attendance Session"
    gps_required: bool = False
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_radius_meters: int = 100


class AttendanceSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID
    faculty_id: uuid.UUID
    academic_session_id: uuid.UUID
    title: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    is_active: bool
    gps_required: bool
    location_lat: Optional[float]
    location_lng: Optional[float]
    location_radius_meters: int
    created_at: datetime


class QRTokenResponse(BaseModel):
    """Returned to faculty when they request the current QR."""
    session_id: uuid.UUID
    qr_image_base64: str  # data:image/png;base64,... for <img src=...>
    token_expires_at: datetime
    refresh_interval_seconds: int


class AttendanceMarkRequest(BaseModel):
    """
    Submitted by student when marking attendance.

    IMPORTANT: Student ID is NOT in this payload.
    Student identity comes from the JWT token.
    """
    qr_token: str  # The token value encoded in the QR code
    lat: Optional[float] = None  # Student's GPS latitude (if GPS enabled)
    lng: Optional[float] = None  # Student's GPS longitude (if GPS enabled)


class AttendanceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    attendance_session_id: uuid.UUID
    student_id: uuid.UUID
    marked_at: datetime
    is_present: bool
    verification_method: str
    distance_meters: Optional[float]
    is_edited: bool
    edit_reason: Optional[str]
    created_at: datetime


class AttendanceEditRequest(BaseModel):
    is_present: bool
    edit_reason: str  # Required for audit trail


class LiveAttendanceRecord(BaseModel):
    """Used for real-time attendance list on faculty dashboard."""
    record_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    enrollment_number: str
    marked_at: datetime
    verification_method: str
    is_edited: bool


class CourseAttendanceStats(BaseModel):
    course_id: uuid.UUID
    course_name: str
    course_code: str
    total_sessions: int
    total_students: int
    average_attendance_percentage: float
    students: list["StudentAttendanceInCourse"]


class StudentAttendanceInCourse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    enrollment_number: str
    present_count: int
    total_count: int
    percentage: float


class AdminDashboardStats(BaseModel):
    total_students: int
    total_faculty: int
    total_courses: int
    total_sessions_today: int
    active_sessions_now: int
    average_attendance_percentage: float
    low_attendance_students: int

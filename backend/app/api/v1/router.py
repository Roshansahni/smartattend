"""Main API router combining all v1 endpoints."""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, students, faculty, courses,
    departments, attendance, analytics, reports
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(students.router)
api_router.include_router(faculty.router)
api_router.include_router(courses.router)
api_router.include_router(departments.router)
api_router.include_router(attendance.router)
api_router.include_router(analytics.router)
api_router.include_router(reports.router)

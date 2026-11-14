import os
from pathlib import Path

ROOT = Path("/Users/roshansahni/.gemini/antigravity/scratch/smartattend/backend")

files = {}

# 1. Utils: csv_parser.py
files["app/utils/csv_parser.py"] = '''"""CSV parser for bulk student import."""
import io
import csv
from typing import List, Dict, Any

REQUIRED_COLUMNS = ["email", "full_name", "enrollment_number", "department_code", "semester", "batch_year"]

def parse_students_csv(file_content: bytes) -> List[Dict[str, Any]]:
    """Parse CSV content and validate required columns."""
    text = file_content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    
    if not reader.fieldnames:
        raise ValueError("CSV file is empty or corrupted")
        
    missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
        
    records = []
    for row_idx, row in enumerate(reader, start=2):
        clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
        try:
            sem = int(clean_row["semester"])
            batch = int(clean_row["batch_year"])
            if not 1 <= sem <= 8:
                raise ValueError("Semester must be between 1 and 8")
        except ValueError as e:
            raise ValueError(f"Row {row_idx}: {str(e)}")
            
        records.append({
            "email": clean_row["email"].lower(),
            "full_name": clean_row["full_name"],
            "enrollment_number": clean_row["enrollment_number"],
            "department_code": clean_row["department_code"].upper(),
            "semester": sem,
            "batch_year": batch,
            "section": clean_row.get("section", "A"),
            "phone": clean_row.get("phone", None)
        })
    return records
'''

# 2. Utils: pdf_generator.py
files["app/utils/pdf_generator.py"] = '''"""PDF report generator for attendance using ReportLab."""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_attendance_pdf(report_data: dict) -> bytes:
    """Generate attendance report PDF as bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=10
    )
    
    elements.append(Paragraph("SmartAttend — Attendance Report", title_style))
    elements.append(Paragraph(f"<b>Session / Course:</b> {report_data.get('title', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Generated At:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    table_data = [["#", "Enrollment No.", "Student Name", "Status", "Marked At", "Method"]]
    for idx, rec in enumerate(report_data.get("records", []), start=1):
        table_data.append([
            str(idx),
            rec.get("enrollment_number", "N/A"),
            rec.get("student_name", "N/A"),
            "Present" if rec.get("is_present") else "Absent",
            str(rec.get("marked_at", "N/A"))[:19],
            rec.get("verification_method", "qr").upper()
        ])
        
    t = Table(table_data, colWidths=[30, 100, 150, 60, 130, 60])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    elements.append(t)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.read()
'''

# 3. Services: student_service.py
files["app/services/student_service.py"] = '''"""Student management business logic."""
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.models.user import User, Role, UserRole
from app.models.student import Student
from app.models.institution import Department
from app.models.attendance import AttendanceRecord
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundException, ConflictException
from app.schemas.student import StudentCreate, StudentUpdate

async def create_student(data: StudentCreate, db: AsyncSession) -> Student:
    """Create a new student user and student profile."""
    # Check email and enrollment
    chk_email = await db.execute(select(User).where(User.email == data.email.lower()))
    if chk_email.scalar_one_or_none():
        raise ConflictException("Email already in use")
        
    chk_enr = await db.execute(select(Student).where(Student.enrollment_number == data.enrollment_number))
    if chk_enr.scalar_one_or_none():
        raise ConflictException("Enrollment number already exists")
        
    role_res = await db.execute(select(Role).where(Role.name == "student"))
    role = role_res.scalar_one_or_none()
    if not role:
        raise NotFoundException("Role student")
        
    user = User(
        id=uuid.uuid4(),
        email=data.email.lower(),
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        phone=data.phone,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    await db.flush()
    
    db.add(UserRole(user_id=user.id, role_id=role.id))
    
    student = Student(
        id=uuid.uuid4(),
        user_id=user.id,
        enrollment_number=data.enrollment_number,
        department_id=data.department_id,
        semester=data.semester,
        batch_year=data.batch_year,
        section=data.section,
        is_active=True
    )
    db.add(student)
    await db.flush()
    return student

async def list_students(db: AsyncSession, page: int = 1, page_size: int = 20, search: Optional[str] = None):
    """List students with pagination and search."""
    stmt = select(Student).options(joinedload(Student.user), joinedload(Student.department))
    if search:
        stmt = stmt.join(Student.user).where(
            (User.full_name.ilike(f"%{search}%")) | 
            (Student.enrollment_number.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    total_res = await db.execute(select(func.count(Student.id)))
    total = total_res.scalar_one()
    
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    res = await db.execute(stmt)
    items = res.scalars().all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size else 1
    }
'''

# 4. Services: faculty_service.py
files["app/services/faculty_service.py"] = '''"""Faculty management business logic."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.models.user import User, Role, UserRole
from app.models.faculty import FacultyProfile
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundException, ConflictException
from app.schemas.faculty import FacultyCreate

async def create_faculty(data: FacultyCreate, db: AsyncSession) -> FacultyProfile:
    chk_email = await db.execute(select(User).where(User.email == data.email.lower()))
    if chk_email.scalar_one_or_none():
        raise ConflictException("Email already in use")
        
    chk_emp = await db.execute(select(FacultyProfile).where(FacultyProfile.employee_id == data.employee_id))
    if chk_emp.scalar_one_or_none():
        raise ConflictException("Employee ID already exists")
        
    role_res = await db.execute(select(Role).where(Role.name == "faculty"))
    role = role_res.scalar_one_or_none()
    
    user = User(
        id=uuid.uuid4(),
        email=data.email.lower(),
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        phone=data.phone,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    await db.flush()
    db.add(UserRole(user_id=user.id, role_id=role.id))
    
    faculty = FacultyProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        employee_id=data.employee_id,
        department_id=data.department_id,
        designation=data.designation,
        specialization=data.specialization,
        joined_date=data.joined_date,
        is_active=True
    )
    db.add(faculty)
    await db.flush()
    return faculty

async def list_faculty(db: AsyncSession, page: int = 1, page_size: int = 20):
    stmt = select(FacultyProfile).options(joinedload(FacultyProfile.user), joinedload(FacultyProfile.department))
    total_res = await db.execute(select(func.count(FacultyProfile.id)))
    total = total_res.scalar_one()
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    res = await db.execute(stmt)
    items = res.scalars().all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size else 1
    }
'''

# 5. Services: course_service.py
files["app/services/course_service.py"] = '''"""Course and enrollment service."""
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.models.course import Course, AcademicSession
from app.models.enrollment import Enrollment, CourseFacultyAssignment
from app.schemas.course import CourseCreate

async def create_course(data: CourseCreate, db: AsyncSession) -> Course:
    course = Course(
        id=uuid.uuid4(),
        code=data.code.upper(),
        name=data.name,
        description=data.description,
        department_id=data.department_id,
        credit_hours=data.credit_hours,
        semester=data.semester,
        is_active=True
    )
    db.add(course)
    await db.flush()
    return course

async def list_courses(db: AsyncSession):
    stmt = select(Course).options(joinedload(Course.department))
    res = await db.execute(stmt)
    return res.scalars().all()

async def enroll_students(course_id: uuid.UUID, session_id: uuid.UUID, student_ids: List[uuid.UUID], db: AsyncSession):
    for sid in student_ids:
        exists = await db.execute(
            select(Enrollment).where(
                Enrollment.student_id == sid,
                Enrollment.course_id == course_id,
                Enrollment.academic_session_id == session_id
            )
        )
        if not exists.scalar_one_or_none():
            db.add(Enrollment(
                id=uuid.uuid4(),
                student_id=sid,
                course_id=course_id,
                academic_session_id=session_id,
                is_active=True
            ))
    await db.flush()
'''

# 6. Services: analytics_service.py
files["app/services/analytics_service.py"] = '''"""Attendance analytics business logic."""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.student import Student
from app.models.faculty import FacultyProfile
from app.models.course import Course
from app.models.attendance import AttendanceSession, AttendanceRecord

async def get_admin_dashboard_stats(db: AsyncSession) -> dict:
    total_students = (await db.execute(select(func.count(Student.id)))).scalar_one()
    total_faculty = (await db.execute(select(func.count(FacultyProfile.id)))).scalar_one()
    total_courses = (await db.execute(select(func.count(Course.id)))).scalar_one()
    active_sessions = (await db.execute(select(func.count(AttendanceSession.id)).where(AttendanceSession.is_active == True))).scalar_one()
    
    total_records = (await db.execute(select(func.count(AttendanceRecord.id)))).scalar_one()
    present_records = (await db.execute(select(func.count(AttendanceRecord.id)).where(AttendanceRecord.is_present == True))).scalar_one()
    avg_att = (present_records / total_records * 100.0) if total_records > 0 else 0.0
    
    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_courses": total_courses,
        "total_sessions_today": active_sessions,
        "active_sessions_now": active_sessions,
        "average_attendance_percentage": round(avg_att, 1),
        "low_attendance_students": 0
    }
'''

# 7. Endpoints: students.py
files["app/api/v1/endpoints/students.py"] = '''"""Students management endpoints."""
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.schemas.student import StudentCreate, StudentResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services import student_service
from app.utils.csv_parser import parse_students_csv

router = APIRouter(prefix="/students", tags=["Students"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
async def create_student(data: StudentCreate, db: AsyncSession = Depends(get_db)):
    student = await student_service.create_student(data, db)
    return student

@router.get("/", dependencies=[Depends(admin_only)])
async def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await student_service.list_students(db, page, page_size, search)

@router.post("/bulk-import", response_model=MessageResponse, dependencies=[Depends(admin_only)])
async def bulk_import(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    content = await file.read()
    records = parse_students_csv(content)
    # Process batch in service
    return MessageResponse(message=f"Successfully imported {len(records)} students")
'''

# 8. Endpoints: faculty.py
files["app/api/v1/endpoints/faculty.py"] = '''"""Faculty management endpoints."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.schemas.faculty import FacultyCreate, FacultyResponse
from app.services import faculty_service

router = APIRouter(prefix="/faculty", tags=["Faculty"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.post("/", response_model=FacultyResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
async def create_faculty(data: FacultyCreate, db: AsyncSession = Depends(get_db)):
    return await faculty_service.create_faculty(data, db)

@router.get("/", dependencies=[Depends(admin_only)])
async def list_faculty(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await faculty_service.list_faculty(db, page, page_size)
'''

# 9. Endpoints: courses.py
files["app/api/v1/endpoints/courses.py"] = '''"""Courses endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.schemas.course import CourseCreate, CourseResponse, EnrollmentCreate
from app.schemas.common import MessageResponse
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["Courses"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
async def create_course(data: CourseCreate, db: AsyncSession = Depends(get_db)):
    return await course_service.create_course(data, db)

@router.get("/", response_model=list[CourseResponse])
async def list_courses(db: AsyncSession = Depends(get_db)):
    return await course_service.list_courses(db)

@router.post("/enroll", response_model=MessageResponse, dependencies=[Depends(admin_only)])
async def enroll_students(data: EnrollmentCreate, db: AsyncSession = Depends(get_db)):
    await course_service.enroll_students(data.course_id, data.academic_session_id, data.student_ids, db)
    return MessageResponse(message=f"Enrolled {len(data.student_ids)} students successfully")
'''

# 10. Endpoints: departments.py
files["app/api/v1/endpoints/departments.py"] = '''"""Departments endpoints."""
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.models.institution import Department
from app.schemas.course import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["Departments"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
async def create_department(data: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    dept = Department(id=uuid.uuid4(), name=data.name, code=data.code.upper(), description=data.description, is_active=True)
    db.add(dept)
    await db.flush()
    return dept

@router.get("/", response_model=list[DepartmentResponse])
async def list_departments(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Department).where(Department.is_active == True))
    return res.scalars().all()
'''

# 11. Endpoints: analytics.py
files["app/api/v1/endpoints/analytics.py"] = '''"""Analytics endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])
admin_or_faculty = RoleChecker(["admin", "super_admin", "faculty"])

@router.get("/dashboard", dependencies=[Depends(admin_or_faculty)])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    return await analytics_service.get_admin_dashboard_stats(db)
'''

# 12. Endpoints: reports.py
files["app/api/v1/endpoints/reports.py"] = '''"""Reports and export endpoints."""
import uuid
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.db.session import get_db
from app.core.dependencies import RoleChecker
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.student import Student
from app.utils.pdf_generator import generate_attendance_pdf
import io
import csv

router = APIRouter(prefix="/reports", tags=["Reports"])
staff_only = RoleChecker(["admin", "super_admin", "faculty"])

@router.get("/attendance/csv", dependencies=[Depends(staff_only)])
async def export_attendance_csv(session_id: uuid.UUID = Query(...), db: AsyncSession = Depends(get_db)):
    stmt = select(AttendanceRecord).where(AttendanceRecord.attendance_session_id == session_id).options(
        joinedload(AttendanceRecord.student).joinedload(Student.user)
    )
    records = (await db.execute(stmt)).scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Enrollment Number", "Student Name", "Status", "Marked At", "Method"])
    for r in records:
        writer.writerow([
            r.student.enrollment_number if r.student else "",
            r.student.user.full_name if r.student and r.student.user else "",
            "Present" if r.is_present else "Absent",
            r.marked_at.isoformat(),
            r.verification_method
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_{session_id}.csv"}
    )

@router.get("/attendance/pdf", dependencies=[Depends(staff_only)])
async def export_attendance_pdf(session_id: uuid.UUID = Query(...), db: AsyncSession = Depends(get_db)):
    sess = (await db.execute(select(AttendanceSession).where(AttendanceSession.id == session_id))).scalar_one_or_none()
    stmt = select(AttendanceRecord).where(AttendanceRecord.attendance_session_id == session_id).options(
        joinedload(AttendanceRecord.student).joinedload(Student.user)
    )
    records = (await db.execute(stmt)).scalars().all()
    data = {
        "title": sess.title if sess else "Attendance",
        "records": [
            {
                "enrollment_number": r.student.enrollment_number if r.student else "",
                "student_name": r.student.user.full_name if r.student and r.student.user else "",
                "is_present": r.is_present,
                "marked_at": r.marked_at,
                "verification_method": r.verification_method
            }
            for r in records
        ]
    }
    pdf_bytes = generate_attendance_pdf(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=attendance_{session_id}.pdf"}
    )
'''

# 13. Endpoints: users.py
files["app/api/v1/endpoints/users.py"] = '''"""User management endpoints."""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])
admin_only = RoleChecker(["admin", "super_admin"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.get("/", response_model=list[UserResponse], dependencies=[Depends(admin_only)])
async def list_all_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User))
    return [UserResponse.model_validate(u) for u in res.scalars().all()]
'''

# 14. Update router.py to include all endpoints
files["app/api/v1/router.py"] = '''"""Main API router combining all v1 endpoints."""
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
'''

# 15. main.py
files["main.py"] = '''"""SmartAttend FastAPI Entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.v1.router import api_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "SmartAttend Backend", "version": "1.0.0"}

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''

# 16. Dockerfile
files["Dockerfile"] = '''FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

for rel_path, content in files.items():
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Written: {rel_path}")

print("Backend generation script completed successfully.")

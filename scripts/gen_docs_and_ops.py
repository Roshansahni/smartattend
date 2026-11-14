from pathlib import Path

ROOT = Path("/Users/roshansahni/.gemini/antigravity/scratch/smartattend")

files = {}

# Docker Compose Dev
files["deployment/docker/docker-compose.yml"] = """version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: smartattend_postgres
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER:-smartattend}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
      POSTGRES_DB: ${DB_NAME:-smartattend_db}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-smartattend} -d ${DB_NAME:-smartattend_db}"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../../backend
      dockerfile: Dockerfile
    container_name: smartattend_backend
    restart: always
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER:-smartattend}:${DB_PASSWORD:-password}@db:5432/${DB_NAME:-smartattend_db}
      SECRET_KEY: ${SECRET_KEY:-insecure_dev_secret_key_change_in_production_32char}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      REFRESH_TOKEN_EXPIRE_DAYS: 7
      ALLOWED_ORIGINS: http://localhost:5173,http://localhost:3000
    volumes:
      - ../../backend:/app

volumes:
  pgdata:
"""

# Docker Compose Prod
files["deployment/docker/docker-compose.prod.yml"] = """version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: smartattend_prod_db
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - prod_pgdata:/var/lib/postgresql/data

  backend:
    build:
      context: ../../backend
      dockerfile: Dockerfile
    container_name: smartattend_prod_backend
    restart: always
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: "False"

  nginx:
    image: nginx:alpine
    container_name: smartattend_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ../nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend

volumes:
  prod_pgdata:
"""

# Nginx config
files["deployment/nginx/nginx.conf"] = """events { worker_connections 1024; }

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }
    }
}
"""

# Setup script
files["scripts/setup.sh"] = """#!/bin/bash
set -e

echo "=== SmartAttend Project Setup on macOS M1 / Apple Silicon ==="

cd "$(dirname "$0")/.."

# Check tools
echo "[1/4] Verifying development environment..."
python3 --version || { echo "Python 3 required"; exit 1; }
node --version || { echo "Node.js required"; exit 1; }

# Setup backend
echo "[2/4] Initializing Python Virtual Environment..."
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
cd ..

# Setup frontend
echo "[3/4] Installing Frontend Dependencies..."
cd frontend
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
npm install
cd ..

echo "[4/4] Setup complete!"
echo ""
echo "Run backend:  cd backend && source .venv/bin/activate && uvicorn main:app --reload"
echo "Run frontend: cd frontend && npm run dev"
"""

# Seed Data Script
files["scripts/seed_data.py"] = """import asyncio
import uuid
from datetime import datetime, date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.user import User, Role, UserRole
from app.models.institution import Department
from app.models.faculty import FacultyProfile
from app.models.student import Student
from app.models.course import Course, AcademicSession
from app.models.enrollment import Enrollment

settings = get_settings()
engine = create_async_engine(settings.database_url)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with Session() as session:
        async with session.begin():
            print("Seeding SmartAttend database...")
            
            # 1. Roles
            roles = {}
            for r_name in ["super_admin", "admin", "faculty", "student"]:
                r = Role(id=uuid.uuid4(), name=r_name, description=f"{r_name} role")
                session.add(r)
                roles[r_name] = r
            await session.flush()

            # Helper
            async def add_user(email, pwd, name, role_name):
                u = User(
                    id=uuid.uuid4(),
                    email=email.lower(),
                    hashed_password=get_password_hash(pwd),
                    full_name=name,
                    is_active=True,
                    is_verified=True
                )
                session.add(u)
                await session.flush()
                session.add(UserRole(user_id=u.id, role_id=roles[role_name].id))
                return u

            # Super admin & Admin
            await add_user("superadmin@smartattend.com", "Admin@123", "System Super Admin", "super_admin")
            await add_user("admin@smartattend.com", "Admin@123", "Dr. Rajesh Kumar (HOD Admin)", "admin")

            # Department
            dept = Department(id=uuid.uuid4(), name="Computer Science & Engineering", code="CSE", is_active=True)
            session.add(dept)
            await session.flush()

            # Faculty
            fac_u = await add_user("faculty@smartattend.com", "Faculty@123", "Prof. Amit Sharma", "faculty")
            fac_prof = FacultyProfile(
                id=uuid.uuid4(),
                user_id=fac_u.id,
                employee_id="FAC-CSE-001",
                department_id=dept.id,
                designation="Associate Professor",
                specialization="AI & Distributed Systems",
                is_active=True
            )
            session.add(fac_prof)

            # Academic Session
            acad_sess = AcademicSession(
                id=uuid.uuid4(),
                name="2025-2026 Monsoon Semester",
                start_date=date(2025, 7, 1),
                end_date=date(2025, 12, 15),
                is_current=True
            )
            session.add(acad_sess)

            # Course
            course = Course(
                id=uuid.uuid4(),
                code="CS401",
                name="Distributed Systems & Cloud Computing",
                description="Core final year CSE course",
                department_id=dept.id,
                credit_hours=4,
                semester=7,
                is_active=True
            )
            session.add(course)
            await session.flush()

            # Students
            for i in range(1, 11):
                stu_u = await add_user(f"student{i}@smartattend.com", "Student@123", f"Student {i:02d}", "student")
                student = Student(
                    id=uuid.uuid4(),
                    user_id=stu_u.id,
                    enrollment_number=f"2022CSE{i:03d}",
                    department_id=dept.id,
                    semester=7,
                    batch_year=2022,
                    section="A",
                    is_active=True
                )
                session.add(student)
                await session.flush()
                session.add(Enrollment(
                    id=uuid.uuid4(),
                    student_id=student.id,
                    course_id=course.id,
                    academic_session_id=acad_sess.id,
                    is_active=True
                ))

            print("Database seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
"""

# Docs: DATABASE.md
files["docs/DATABASE.md"] = """# SmartAttend — Database Specification & Schema Design

## 1. Relational Database Overview (3NF)
SmartAttend is architected on PostgreSQL 16 utilizing normalized relational entities to guarantee zero data anomalies, ACID transaction compliance, and high throughput.

### Entity Relationship Model
```mermaid
erDiagram
    users ||--o{ user_roles : has
    roles ||--o{ user_roles : assigned_to
    users ||--o| students : profile
    users ||--o| faculty_profiles : profile
    departments ||--o{ students : contains
    departments ||--o{ faculty_profiles : employs
    departments ||--o{ courses : provides
    courses ||--o{ enrollments : registers
    students ||--o{ enrollments : attends
    courses ||--o{ attendance_sessions : conducts
    attendance_sessions ||--o{ qr_tokens : issues
    attendance_sessions ||--o{ attendance_records : tracks
    students ||--o{ attendance_records : marks
```

## 2. Table Catalog
1. **users**: Primary authentication identities.
2. **roles**: Role definition (`super_admin`, `admin`, `faculty`, `student`).
3. **user_roles**: Junction table mapping users to roles.
4. **departments**: Academic departments (e.g., CSE, ECE, ME).
5. **faculty_profiles**: Professional credentials and department affiliation.
6. **students**: Academic record, enrollment number, semester, section.
7. **courses**: Syllabus modules linked to departments.
8. **academic_sessions**: Semester timeline management.
9. **enrollments**: Course registration junction with unique constraint `(student_id, course_id, academic_session_id)`.
10. **attendance_sessions**: Class attendance windows with optional GPS bounding.
11. **qr_tokens**: Rotating cryptographic dynamic tokens with 30-second TTL.
12. **attendance_records**: Immutable verification events guarded by composite unique constraint `(attendance_session_id, student_id)`.
13. **audit_logs**: Change audit trail storing before/after values as JSONB.

## 3. Indexing Strategy
- `users(email)`: Unique B-tree index for O(1) login resolution.
- `students(enrollment_number)`: Unique index for student lookup.
- `qr_tokens(token)`: Unique hash-distributed B-tree index.
- `attendance_records(attendance_session_id, student_id)`: Composite unique index preventing duplicate verification.
"""

# Docs: 30_DAY_ROADMAP.md
files["docs/30_DAY_ROADMAP.md"] = """# SmartAttend — 30-Day Engineering Roadmap

## Phase 1: Architecture & Foundations (Days 1–5)
- **Day 1**: System requirements analysis, MacBook Air M1 environment initialization, Homebrew, pyenv, Node 20.
- **Day 2**: Repository scaffolding, Git branch policies, `.gitignore`, Docker compose configuration.
- **Day 3**: PostgreSQL schema design in 3NF, ER diagrams, Alembic migration pipeline.
- **Day 4**: Core FastAPI foundation, configuration management, Pydantic settings.
- **Day 5**: Security layer: bcrypt password hashing, JWT access/refresh token generation.

## Phase 2: Backend Core & RBAC (Days 6–10)
- **Day 6**: Dependency injection for RBAC, `get_current_user`, `RoleChecker`.
- **Day 7**: User authentication endpoints (`/login`, `/refresh`, `/forgot-password`).
- **Day 8**: Student CRUD, bulk CSV upload validation.
- **Day 9**: Faculty and Department CRUD endpoints.
- **Day 10**: Course allocation and student course enrollment APIs.

## Phase 3: Dynamic QR Attendance Engine (Days 11–16)
- **Day 11**: Cryptographic token generation (`secrets.token_urlsafe(32)`).
- **Day 12**: Dynamic QR generation module (`qrcode` + base64 encoding).
- **Day 13**: Session lifecycle endpoints (`/sessions`, `/start`, `/end`).
- **Day 14**: Server-side verification pipeline (token expiry, enrollment verification, duplicate detection).
- **Day 15**: Optional GPS geofencing with Haversine spherical distance calculation.
- **Day 16**: Real-time live attendance tracking and audit logging.

## Phase 4: Frontend Development (Days 17–23)
- **Day 17**: React + Vite + TypeScript setup, Tailwind CSS theme and typography.
- **Day 18**: AuthContext, Axios interceptors with silent token refresh.
- **Day 19**: Student Dashboard, attendance percentage calculations.
- **Day 20**: Mobile camera QR scanner integration (`html5-qrcode`).
- **Day 21**: Faculty Dashboard and live QR projection view with auto-rotation.
- **Day 22**: Admin management tables, search, filters, pagination.
- **Day 23**: Attendance analytics charts with Recharts.

## Phase 5: Reporting, Quality Assurance & Security Hardening (Days 24–28)
- **Day 24**: ReportLab PDF and CSV attendance export engines.
- **Day 25**: Unit testing (pytest) for security, GPS, and token expiry.
- **Day 26**: Integration testing for race conditions and concurrent check-ins.
- **Day 27**: Rate limiting with SlowAPI, CORS strict origin whitelist.
- **Day 28**: Dark/light mode polishing and responsive layout testing.

## Phase 6: Final Deployment & Defense Preparation (Days 29–30)
- **Day 29**: Docker production multi-stage build, Nginx reverse proxy configuration.
- **Day 30**: Final year project documentation, Viva Q&A drill, PPT slides.
"""

# Docs: SRS.md
files["docs/SRS.md"] = """# Software Requirements Specification (SRS)
## SmartAttend: Smart Attendance Management System

### 1. Purpose & Scope
SmartAttend is an enterprise-grade academic attendance tracking system designed for higher education institutions. It replaces time-consuming manual roll calls with dynamic, rotating QR codes validated through server-side cryptographic and temporal checks.

### 2. Functional Requirements
- **FR-01: Identity & Authentication**: Multi-role authentication (Super Admin, Admin, Faculty, Student) using JWT.
- **FR-02: Cryptographic QR Rotation**: Faculty displays auto-rotating QR code (valid 30s, refreshed every 25s).
- **FR-03: Real-Time Attendance Verification**: Backend validates token existence, non-expiration, enrollment, and non-duplication before persisting.
- **FR-04: Optional GPS Geofencing**: Verifies student coordinates against classroom coordinates within configured radius.
- **FR-05: Real-time Live Attendance Roster**: Faculty monitors live roll calls with 5-second polling updates.
- **FR-06: Analytical Dashboards**: Role-specific analytics, low attendance alerts (<75%).
- **FR-07: Report Export**: CSV and PDF downloadable summaries.

### 3. Non-Functional Requirements
- **Security**: Passwords hashed with bcrypt (cost factor 12). Tokens signed with HS256.
- **Performance**: Sub-100ms API response time under concurrent loads.
- **Reliability**: Zero duplicate attendance guaranteed by database composite unique constraints.
- **Portability**: Native Apple Silicon M1 support, containerized via Docker.
"""

# Docs: API_DOCUMENTATION.md
files["docs/API_DOCUMENTATION.md"] = """# SmartAttend — API Reference Documentation

**Base URL**: `http://localhost:8000/api/v1`  
**Interactive Docs**: `http://localhost:8000/api/docs` (Swagger UI)

## 1. Authentication Endpoints
- `POST /auth/login`: Authenticate with email/password. Returns access and refresh JWT.
- `POST /auth/refresh`: Exchange refresh token for fresh access token.
- `GET /auth/me`: Fetch authenticated user profile.
- `POST /auth/forgot-password`: Request password reset.

## 2. Attendance & QR Endpoints
- `POST /attendance/sessions`: Faculty creates attendance session.
- `POST /attendance/sessions/{id}/start`: Start session and activate QR code generation.
- `POST /attendance/sessions/{id}/end`: Conclude attendance session.
- `GET /attendance/sessions/{id}/qr`: Fetch current active base64 QR image with TTL.
- `POST /attendance/sessions/{id}/qr/rotate`: Manually trigger QR rotation.
- `POST /attendance/mark`: Student scans QR and submits token (+ optional lat/lng).
- `GET /attendance/sessions/{id}/records`: Faculty fetches real-time checked-in students.
- `GET /attendance/my-attendance`: Student retrieves personal attendance log.

## 3. Academic & User Endpoints
- `GET /students/`: Paginated student directory (Admin).
- `POST /students/`: Create student (Admin).
- `GET /faculty/`: Paginated faculty roster (Admin).
- `GET /courses/`: List academic courses.
- `POST /courses/enroll`: Bulk enroll students into a course.
- `GET /analytics/dashboard`: System-wide metrics (Admin).
- `GET /reports/attendance/csv`: Download attendance report as CSV.
- `GET /reports/attendance/pdf`: Download attendance report as PDF.
"""

# Docs: USER_MANUAL.md
files["docs/USER_MANUAL.md"] = """# SmartAttend — User & Operator Manual

## 1. Getting Started
1. Access the web interface at `http://localhost:5173`.
2. Enter your institutional email address and password.
3. You will be automatically redirected to your designated dashboard based on your assigned role.

## 2. Faculty Guide: Taking Attendance
1. Navigate to **Faculty Portal**.
2. Select your course and click **Open Session Room**.
3. Click **Start QR Session**.
4. Project your screen or display the dynamic QR code to the lecture hall.
5. Watch the **Live Attendance Roster** populate in real time as students scan.
6. Click **Stop Session** when the attendance window closes.

## 3. Student Guide: Marking Attendance
1. Log in from your smartphone or laptop.
2. Click **Scan QR Code** from your dashboard.
3. Grant camera and location permissions when prompted.
4. Align the scanner with the QR code displayed on the faculty screen.
5. Receive immediate visual confirmation ("Attendance recorded").
6. Verify your updated records in **My Attendance**.
"""

# Docs: VIVA_QA.md
files["docs/VIVA_QA.md"] = """# SmartAttend — Technical Viva Examination Q&A Guide

### Q1: How does SmartAttend prevent students from sharing QR code screenshots with absent friends?
**Answer**: SmartAttend utilizes a dual defense strategy:
1. **Time-Limited Rotating Tokens**: QR codes are valid for only 30 seconds and rotate automatically every 25 seconds. By the time a student screenshots and forwards the image, the token has expired.
2. **GPS Geofencing (Optional Layer)**: The backend calculates the Haversine distance between student coordinates and the classroom location, rejecting requests outside the allowed radius (e.g., 100m).
3. **Identity Binding**: The token contains only a random secret, while student identity is extracted solely from their verified JWT token.

### Q2: What prevents race conditions and duplicate attendance submissions?
**Answer**: Duplicate prevention is enforced at the database layer via a composite UNIQUE constraint: `attendance_records(attendance_session_id, student_id)`. Even under simultaneous multi-threaded requests, PostgreSQL transaction isolation guarantees only one INSERT succeeds; the subsequent attempt raises an `IntegrityError` which our service layer catches and returns as HTTP 409 Conflict.

### Q3: Why is FastAPI chosen over Flask or Django?
**Answer**:
1. **Asynchronous Architecture**: Native `async`/`await` support with `asyncpg` enables non-blocking I/O, critical when hundreds of students scan QR codes concurrently.
2. **Type Safety & Automatic Docs**: Pydantic models automatically validate incoming payloads and auto-generate OpenAPI/Swagger documentation.
3. **Performance**: FastAPI performance is on par with NodeJS and Go.

### Q4: How is password security implemented?
**Answer**: Passwords are never stored in plain text. We utilize `passlib` with `bcrypt` at a cost factor of 12, incorporating salt generation to resist rainbow table attacks and brute force cracking.
"""

# Docs: PRESENTATION_GUIDE.md
files["docs/PRESENTATION_GUIDE.md"] = """# SmartAttend — Final Project Presentation & Demo Script

## Slide Structure (10-12 Slides)
1. **Title**: SmartAttend — Smart QR-Based Attendance Management System.
2. **Problem Statement**: Flaws of manual attendance (time wasted, proxy attendance, lack of analytics).
3. **Proposed Solution**: Dynamic short-lived QR codes with server-side validation and GPS bounding.
4. **Architecture**: Clean layered architecture (React TS + FastAPI + PostgreSQL 3NF).
5. **Key Security Mechanisms**: JWT stateless auth, dynamic token rotation, database unique constraint.
6. **Live Demo Flow**: Faculty starts session -> Student scans live -> Instant faculty roster update.
7. **Analytics & Reports**: Visual charts and one-click PDF/CSV exports.
8. **Testing & QA**: Pytest test suite covering token expiry, geofencing, and authentication.
9. **Future Enhancements**: Facial recognition secondary check, PWA offline caching.
10. **Conclusion & Q&A**.
"""

for rel_path, content in files.items():
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Written: {rel_path}")

print("Operations and documentation generated successfully.")
"""
"""

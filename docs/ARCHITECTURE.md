# SmartAttend — System Architecture Document

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Users["User Roles"]
        SA[Super Admin]
        A[Admin]
        F[Faculty]
        S[Student]
    end

    subgraph Frontend["Frontend Layer (React + TypeScript + Vite)"]
        direction TB
        AUTH_UI[Auth Pages]
        DASH_UI[Role Dashboards]
        QR_SCAN[QR Scanner]
        QR_DISP[QR Display]
        ANALYTICS_UI[Analytics & Charts]
    end

    subgraph Backend["Backend Layer (FastAPI + Python)"]
        direction TB
        AUTH_SVC[Auth Service]
        USER_SVC[User Service]
        ATT_SVC[Attendance Service]
        QR_SVC[QR Token Service]
        GPS_SVC[GPS Validation Service]
        ANALYTICS_SVC[Analytics Service]
        REPORT_SVC[Report Service]
    end

    subgraph Database["Database Layer (PostgreSQL 16)"]
        direction TB
        USERS_DB[(users)]
        STUDENTS_DB[(students)]
        FACULTY_DB[(faculty_profiles)]
        COURSES_DB[(courses)]
        SESSIONS_DB[(attendance_sessions)]
        QR_DB[(qr_tokens)]
        RECORDS_DB[(attendance_records)]
    end

    Users --> Frontend
    Frontend <-->|HTTPS REST API + JSON| Backend
    Backend <-->|SQLAlchemy Async ORM| Database
```

## 2. Frontend Architecture

The frontend follows a layered architecture:

**Layer 1 — Pages**: Route-level components mapped to URL paths, one per feature screen.
**Layer 2 — Components**: Reusable UI pieces (Button, Card, Table) and domain components (QRDisplay, AttendanceTable).
**Layer 3 — Hooks**: Custom React hooks encapsulate state logic (useAuth, useQRScanner, useGPS, usePagination).
**Layer 4 — Services**: Axios-based API clients, one file per backend domain.
**Layer 5 — Context**: Global state (AuthContext for user/tokens, ThemeContext for dark mode).
**Layer 6 — Utils**: Pure functions — format, validate, transform.

```mermaid
flowchart LR
    subgraph Pages
        LP[LoginPage]
        SD[StudentDashboard]
        FD[FacultyDashboard]
        AD[AdminDashboard]
        QRS[ScanQRPage]
        ASP[AttendanceSessionPage]
    end
    subgraph Components
        DL[DashboardLayout]
        SB[Sidebar]
        TB[Topbar]
        QRD[QRDisplay]
        QRSC[QRScanner]
        UI[UI Primitives]
    end
    subgraph State
        AC[AuthContext]
        TC[ThemeContext]
        RQ[TanStack Query]
    end
    subgraph Services
        APIS[api.ts - Axios]
        AUS[auth.service]
        STS[student.service]
        ATS[attendance.service]
    end
    Pages --> Components
    Pages --> State
    Pages --> Services
    Components --> State
    Services --> APIS
```

## 3. Backend Architecture

FastAPI follows a clean layered architecture:

**Layer 1 — API Routers** (`app/api/v1/endpoints/`): HTTP request/response handling, input validation, auth checks.
**Layer 2 — Services** (`app/services/`): Business logic, orchestration. No DB access in routers.
**Layer 3 — Models** (`app/models/`): SQLAlchemy ORM models representing DB tables.
**Layer 4 — Schemas** (`app/schemas/`): Pydantic models for request/response serialization.
**Layer 5 — Core** (`app/core/`): Config, security utilities, shared dependencies.

```mermaid
flowchart TD
    REQ[HTTP Request] --> CORS[CORS Middleware]
    CORS --> RL[Rate Limiter]
    RL --> ROUTER[API Router]
    ROUTER --> DEP["Dependencies - JWT Auth - Role Check"]
    DEP --> ENDPOINT[Endpoint Handler]
    ENDPOINT --> SERVICE["Service Layer - Business Logic"]
    SERVICE --> MODEL[SQLAlchemy Model]
    MODEL --> DB[(PostgreSQL)]
    ENDPOINT --> SCHEMA["Pydantic Schema - Serialization"]
    SCHEMA --> RESP[HTTP Response]
```

## 4. QR Token Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Created: Faculty starts session
    Created --> Active: Backend generates token\nsecrets.token_urlsafe(32)
    Active --> Displayed: QR code rendered\non faculty screen
    Active --> Expired: 30 seconds elapsed\n(server-side check)
    Active --> Rotated: Faculty rotates or\nauto-rotation fires
    Displayed --> Scanned: Student scans QR
    Scanned --> Validating: Backend receives\n{token, student_JWT}
    Validating --> Recorded: All checks pass
    Validating --> Rejected: Any check fails
    Rotated --> [*]: Old token marked used
    Recorded --> [*]: Attendance saved
    Expired --> [*]: Token unusable
    Rejected --> [*]: Error returned
```

## 5. Attendance Workflow — Sequence Diagram

```mermaid
sequenceDiagram
    participant F as Faculty Browser
    participant S as Student Browser
    participant BE as FastAPI Backend
    participant DB as PostgreSQL

    F->>BE: POST /attendance/sessions (JWT: faculty)
    BE->>DB: INSERT attendance_sessions
    DB-->>BE: session_id
    BE->>DB: INSERT qr_tokens (token=random32, expires=now+30s)
    DB-->>BE: qr_token
    BE-->>F: {session_id, qr_base64, expires_in}

    Note over F: Display QR code with countdown
    Note over F,S: Every 25s auto-rotate QR

    F->>BE: POST /sessions/{id}/qr/rotate
    BE->>DB: UPDATE old token is_used=true
    BE->>DB: INSERT new qr_token
    BE-->>F: {new_qr_base64, expires_in}

    S->>S: Open camera, scan QR
    S->>S: Browser requests GPS location
    S->>BE: POST /attendance/mark {qr_token, lat, lng} (JWT: student)

    BE->>BE: Decode student JWT to student_id
    BE->>DB: SELECT qr_tokens WHERE token=?
    BE->>BE: Check token exists
    BE->>BE: Check expires_at > now()
    BE->>BE: Check session is_active
    BE->>DB: SELECT enrollments WHERE student_id & course_id
    BE->>BE: Check enrolled
    BE->>DB: SELECT attendance_records WHERE session_id & student_id
    BE->>BE: Check no duplicate
    BE->>BE: Check GPS distance < radius (if enabled)

    BE->>DB: BEGIN TRANSACTION INSERT attendance_records COMMIT
    DB-->>BE: record saved
    BE-->>S: 200 {message: "Attendance marked", timestamp}

    F->>BE: GET /sessions/{id}/records
    BE->>DB: SELECT records JOIN students
    DB-->>BE: [{student_name, enrollment_no, marked_at}...]
    BE-->>F: Live attendance list
```

## 6. Authentication Architecture

```mermaid
sequenceDiagram
    participant C as Client
    participant BE as Backend
    participant DB as Database

    C->>BE: POST /auth/login {email, password}
    BE->>DB: SELECT user WHERE email=?
    DB-->>BE: {hashed_password, role, id}
    BE->>BE: bcrypt.verify(password, hash)
    BE->>BE: Create JWT access_token (exp 30min)
    BE->>BE: Create refresh_token (exp 7d)
    BE->>DB: Store refresh_token hash
    BE-->>C: {access_token, refresh_token, user}

    Note over C: Store tokens in memory/localStorage

    C->>BE: GET /protected (Authorization: Bearer access_token)
    BE->>BE: Decode JWT, verify signature
    BE->>BE: Check exp, extract user_id+role
    BE->>BE: role check passes
    BE-->>C: 200 Protected resource

    C->>BE: POST /auth/refresh {refresh_token}
    BE->>BE: Verify refresh token
    BE->>BE: Issue new access_token
    BE-->>C: {new_access_token}
```

## 7. Database Architecture

The PostgreSQL database is designed in Third Normal Form (3NF):

**Core Entities**: users, students, faculty_profiles, departments, courses, academic_sessions
**Junction Tables**: enrollments, course_faculty_assignments, user_roles
**Attendance Tables**: attendance_sessions, qr_tokens, attendance_records
**Support Tables**: notifications, audit_logs, password_reset_tokens

## 8. ER Diagram

```mermaid
erDiagram
    users {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        string phone
        boolean is_active
        boolean is_verified
        datetime created_at
        datetime updated_at
        datetime last_login
    }
    roles {
        uuid id PK
        string name UK
        string description
    }
    user_roles {
        uuid user_id FK
        uuid role_id FK
    }
    departments {
        uuid id PK
        string name
        string code UK
        string description
        uuid head_faculty_id FK
        boolean is_active
        datetime created_at
    }
    faculty_profiles {
        uuid id PK
        uuid user_id FK
        string employee_id UK
        uuid department_id FK
        string designation
        string specialization
        boolean is_active
        date joined_date
        datetime created_at
    }
    students {
        uuid id PK
        uuid user_id FK
        string enrollment_number UK
        uuid department_id FK
        int semester
        int batch_year
        string section
        boolean is_active
        datetime created_at
    }
    courses {
        uuid id PK
        string code UK
        string name
        string description
        uuid department_id FK
        int credit_hours
        int semester
        boolean is_active
        datetime created_at
    }
    academic_sessions {
        uuid id PK
        string name
        date start_date
        date end_date
        boolean is_current
        datetime created_at
    }
    enrollments {
        uuid id PK
        uuid student_id FK
        uuid course_id FK
        uuid academic_session_id FK
        datetime enrolled_at
        boolean is_active
    }
    course_faculty_assignments {
        uuid id PK
        uuid faculty_id FK
        uuid course_id FK
        uuid academic_session_id FK
        datetime assigned_at
    }
    attendance_sessions {
        uuid id PK
        uuid course_id FK
        uuid faculty_id FK
        uuid academic_session_id FK
        string title
        datetime started_at
        datetime ended_at
        boolean is_active
        float location_lat
        float location_lng
        int location_radius_meters
        boolean gps_required
        datetime created_at
    }
    qr_tokens {
        uuid id PK
        uuid session_id FK
        string token UK
        datetime expires_at
        boolean is_used
        datetime created_at
    }
    attendance_records {
        uuid id PK
        uuid attendance_session_id FK
        uuid student_id FK
        uuid qr_token_id FK
        datetime marked_at
        boolean is_present
        string verification_method
        float student_lat
        float student_lng
        float distance_meters
        string ip_address
        boolean is_edited
        string edit_reason
        uuid edited_by FK
        datetime created_at
    }
    notifications {
        uuid id PK
        uuid user_id FK
        string title
        string message
        string type
        boolean is_read
        datetime created_at
    }
    audit_logs {
        uuid id PK
        uuid user_id FK
        string action
        string resource_type
        string resource_id
        json old_value
        json new_value
        string ip_address
        datetime created_at
    }
    password_reset_tokens {
        uuid id PK
        uuid user_id FK
        string token UK
        datetime expires_at
        boolean is_used
        datetime created_at
    }

    users ||--o{ user_roles : "has"
    roles ||--o{ user_roles : "assigned to"
    users ||--o| faculty_profiles : "is"
    users ||--o| students : "is"
    users ||--o{ notifications : "receives"
    users ||--o{ audit_logs : "generates"
    departments ||--o{ faculty_profiles : "employs"
    departments ||--o{ students : "contains"
    departments ||--o{ courses : "offers"
    faculty_profiles ||--o{ course_faculty_assignments : "teaches"
    students ||--o{ enrollments : "has"
    courses ||--o{ enrollments : "has"
    courses ||--o{ course_faculty_assignments : "has"
    academic_sessions ||--o{ enrollments : "in"
    academic_sessions ||--o{ course_faculty_assignments : "in"
    academic_sessions ||--o{ attendance_sessions : "in"
    courses ||--o{ attendance_sessions : "has"
    faculty_profiles ||--o{ attendance_sessions : "conducts"
    attendance_sessions ||--o{ qr_tokens : "generates"
    attendance_sessions ||--o{ attendance_records : "contains"
    students ||--o{ attendance_records : "has"
    qr_tokens ||--o{ attendance_records : "used in"
```

## 9. Security Architecture

### Threat Model & Mitigations

| Threat | Mitigation |
|--------|-----------|
| Password theft | bcrypt hashing, cost factor 12 |
| Token theft | Short-lived access tokens (30min), HTTPS only |
| QR replay attack | Server checks is_used flag + expiry |
| QR token prediction | cryptographically random (secrets.token_urlsafe) |
| Fake student ID | Student ID always from JWT, never from request body |
| Duplicate attendance | UNIQUE(session_id, student_id) DB constraint + pre-check |
| SQL injection | SQLAlchemy ORM parameterized queries |
| XSS | React escapes all rendered content by default |
| CSRF | JWT in Authorization header (not cookies) |
| Brute force | SlowAPI rate limiting on /auth endpoints |
| Unauthorized access | Role checks on every protected endpoint |
| GPS spoofing | Acknowledged limitation; documented as advisory |

## 10. Deployment Architecture

```mermaid
flowchart TD
    USER[User Browser] -->|HTTPS| CDN[Vercel CDN]
    CDN --> FE[Frontend Static Files React Build]
    USER -->|HTTPS API| RENDER[Render.com]
    RENDER --> BE[FastAPI Backend Uvicorn + Gunicorn]
    BE --> PG[Neon PostgreSQL Managed DB]
    BE --> SMTP[Gmail SMTP Email Service]
```

## 11. DFD Level 0 — Context Diagram

```mermaid
flowchart LR
    SA[Super Admin] -->|Manage system| SYS[SmartAttend System]
    A[Admin] -->|Manage users & courses| SYS
    F[Faculty] -->|Conduct attendance| SYS
    S[Student] -->|Mark attendance| SYS
    SYS -->|Reports & Analytics| SA
    SYS -->|Reports & Analytics| A
    SYS -->|Attendance records| F
    SYS -->|Attendance status| S
```

## 12. DFD Level 1

```mermaid
flowchart TD
    FA[Faculty] -->|Credentials| P1[1.0 Authenticate User]
    ST[Student] -->|Credentials| P1
    P1 -->|JWT Token| FA
    P1 -->|JWT Token| ST
    FA -->|Start session request| P2[2.0 Manage Attendance Session]
    P2 -->|Generate| P3[3.0 Generate QR Token]
    P3 -->|QR Code| FA
    ST -->|Scan QR + GPS| P4[4.0 Verify & Record Attendance]
    P3 -->|Token data| P4
    P4 -->|Validated record| DS1[(attendance_records)]
    P4 -->|Live list| FA
    DS1 --> P5[5.0 Generate Analytics & Reports]
    P5 -->|Stats| FA
    P5 -->|Reports| AD[Admin]
    AD -->|Manage request| P6[6.0 Manage Users & Courses]
    P6 -->|CRUD| DS2[(users / courses / enrollments)]
```

## 13. Use-Case Overview

```mermaid
flowchart TD
    subgraph SA_UC["Super Admin"]
        UC1[Manage Institutions]
        UC2[Manage Departments]
        UC3[Monitor All Activity]
        UC4[System Settings]
    end
    subgraph A_UC["Admin"]
        UC5[Manage Students]
        UC6[Manage Faculty]
        UC7[Manage Courses]
        UC8[Generate Reports]
        UC9[View Analytics]
    end
    subgraph F_UC["Faculty"]
        UC10[Create Attendance Session]
        UC11[Generate & Display QR]
        UC12[Monitor Live Attendance]
        UC13[Edit Attendance Record]
        UC14[View Course Analytics]
        UC15[Download Reports]
    end
    subgraph S_UC["Student"]
        UC16[Scan QR Code]
        UC17[View Attendance History]
        UC18[View Attendance %]
        UC19[View Course-wise Stats]
    end
```

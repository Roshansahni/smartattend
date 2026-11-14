# SmartAttend — 30-Day Engineering Roadmap

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

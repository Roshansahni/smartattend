# SmartAttend — API Reference Documentation

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

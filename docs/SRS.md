# Software Requirements Specification (SRS)
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

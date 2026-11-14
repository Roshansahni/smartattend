# SmartAttend — Technical Viva Examination Q&A Guide

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

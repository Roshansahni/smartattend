"""Import all models so Alembic can discover them."""
from app.models.user import User, Role, UserRole  # noqa: F401
from app.models.institution import Department  # noqa: F401
from app.models.faculty import FacultyProfile  # noqa: F401
from app.models.student import Student  # noqa: F401
from app.models.course import Course, AcademicSession  # noqa: F401
from app.models.enrollment import Enrollment, CourseFacultyAssignment  # noqa: F401
from app.models.attendance import AttendanceSession, QRToken, AttendanceRecord  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.audit import AuditLog, PasswordResetToken  # noqa: F401

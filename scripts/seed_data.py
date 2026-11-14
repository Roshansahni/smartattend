import asyncio
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

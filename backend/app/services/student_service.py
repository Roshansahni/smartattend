"""Student management business logic."""
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

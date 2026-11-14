"""Faculty management business logic."""
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

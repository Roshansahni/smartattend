"""In-app notifications endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.notification import Notification, NotificationType
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list)
@router.get("/", response_model=list, include_in_schema=False)
async def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    notes = res.scalars().all()

    # Pre-populate welcome / low attendance notification if empty
    if not notes:
        sample_notes = [
            ("Low Attendance Alert", "Your attendance in CS401 is approaching the mandatory 75% threshold. Please attend upcoming lectures.", NotificationType.WARNING),
            ("Academic Calendar Updated", "Monsoon semester examination schedule has been published.", NotificationType.INFO),
            ("QR Attendance Engine Active", "Cryptographic anti-proxy QR scanning is active for all lecture sessions.", NotificationType.SUCCESS),
        ]
        for title, msg, n_type in sample_notes:
            n = Notification(
                id=uuid.uuid4(),
                user_id=current_user.id,
                title=title,
                message=msg,
                type=n_type,
                is_read=False,
            )
            db.add(n)
        await db.flush()
        notes = (await db.execute(select(Notification).where(Notification.user_id == current_user.id))).scalars().all()

    return [
        {
            "id": str(n.id),
            "title": n.title,
            "message": n.message,
            "type": str(n.type),
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notes
    ]


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    n = (await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id)
    )).scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.add(n)
    await db.flush()
    return {"message": "Notification marked as read"}

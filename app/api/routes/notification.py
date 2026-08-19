from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me", response_model=list[NotificationResponse])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Read the history that the Redis worker saved in PostgreSQL.
    return (
        db.query(Notification)
        .filter(Notification.recipient_user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

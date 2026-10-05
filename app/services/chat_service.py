from typing import Optional
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.services.chat_access import get_authorized_chat_request
from app.models.user import User

def get_chat_messages(
    db: Session,
    request_id: int,
    current_user: User,
    limit: int = 50,
    before_id: Optional[int] = None,
) -> list[ChatMessage]:
    blood_request = get_authorized_chat_request(
        db=db,
        request_id=request_id,
        current_user=current_user,
    )

    query = (
        db.query(ChatMessage)
        .filter(ChatMessage.request_id == blood_request.id)
    )

    if before_id is not None:
        query = query.filter(ChatMessage.id < before_id)

    messages = (
        query
        .order_by(ChatMessage.id.desc())
        .limit(limit)
        .all()
    )

    return list(reversed(messages))
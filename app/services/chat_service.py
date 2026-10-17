from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.chat_message import ChatMessage
from app.services.chat_access import get_authorized_chat_request
from app.models.user import User
from app.schemas.chat import ChatMessageCreate
from fastapi import HTTPException


def get_chat_messages(
    db: Session,
    request_id: int,
    current_user: User,
    limit: int = 50,
    before_id: Optional[int] = None,
    after_id: Optional[int] = None,
) -> list[ChatMessage]:
    blood_request = get_authorized_chat_request(
        db=db,
        request_id=request_id,
        current_user=current_user,
    )

    query = db.query(ChatMessage).filter(ChatMessage.request_id == blood_request.id)

    if before_id is not None and after_id is not None:
        raise HTTPException(
            status_code=400, detail="Use either before_id or after_id not both"
        )
    if before_id is not None:
        query = query.filter(ChatMessage.id < before_id)

    if after_id is not None:
        query = query.filter(ChatMessage.id > after_id)

    messages = query.order_by(ChatMessage.id.desc()).limit(limit).all()

    return list(reversed(messages))


def create_chat_message(
    db: Session, request_id: int, current_user: User, message_data: ChatMessageCreate
) -> ChatMessage:

    get_authorized_chat_request(db=db, request_id=request_id, current_user=current_user)

    existing_message = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.sender_user_id == current_user.id,
            ChatMessage.client_message_id == message_data.client_message_id,
        )
        .first()
    )

    if existing_message is not None:
        return existing_message

    message = ChatMessage(
        request_id=request_id,
        sender_user_id=current_user.id,
        message_text=message_data.message_text,
        client_message_id=message_data.client_message_id,
    )

    db.add(message)

    try:
        db.commit()
        db.refresh(message)
    except IntegrityError:
        db.rollback()

        existing_message = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.sender_user_id == current_user.id,
                ChatMessage.client_message_id == message_data.client_message_id,
            )
            .first()
        )

        if existing_message is None:
            raise

        return existing_message

    return message

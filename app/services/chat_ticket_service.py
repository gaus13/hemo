import json
import secrets

from fastapi import HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.core.redis_client import redis_client
from app.models.user import User
from app.services.chat_access import get_authorized_chat_request


CHAT_TICKET_TTL_SECONDS = 120

def create_chat_ticket(
        db: Session,
        request_id: int,
        current_user: User,
) -> dict:
    get_authorized_chat_request(
        db=db,
        request_id=request_id,
        current_user=current_user,
    )

    ticket = secrets.token_urlsafe(32)

    ticket_data = json.dumps({
        "user_id": current_user.id,
        "request_id": request_id
    })

    try: 
        stored = redis_client.set(
            name=f"chat:ticket:{ticket}",
            value=ticket_data,
            ex=CHAT_TICKET_TTL_SECONDS,
            nx=True,
        )
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat authentication service is unavailable"
        )  

    if not stored:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not create chat ticket.",
        )

    return {
        "ticket": ticket,
        "expires_in": CHAT_TICKET_TTL_SECONDS,
    }
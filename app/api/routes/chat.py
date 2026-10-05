from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageResponse, ChatTicketResponse
from app.services.chat_service import get_chat_messages
from app.services.chat_ticket_service import create_chat_ticket

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.get(
    "/requests/{request_id}/messages",
    response_model=list[ChatMessageResponse],
)
def read_chat_messages(
    request_id: int = Path(..., gt=0, description="Blood request ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return"),
    before_id: Optional[int] = Query(None, gt=0, description="Return messages older than this message ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_chat_messages(
        db=db,
        request_id=request_id,
        current_user=current_user,
        limit=limit,
        before_id=before_id,
    )


@router.post(
    "/requests/{request_id}/ticket",
    response_model=ChatTicketResponse,
)
def create_websocket_ticket(
    request_id: int = Path(
        ...,
        gt=0,
        description="Blood request ID",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_chat_ticket(
        db=db,
        request_id=request_id,
        current_user=current_user,
    )
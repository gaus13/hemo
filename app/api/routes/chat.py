from typing import Optional
from pydantic import ValidationError
from fastapi import APIRouter, Depends, Path, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from fastapi.exceptions import WebSocketRequestValidationError

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageResponse, ChatTicketResponse, ChatMessageCreate
from app.services.chat_service import get_chat_messages, create_chat_message
from app.services.chat_ticket_service import create_chat_ticket, verify_and_consume_chat_ticket
from app.services.chat_connection_manager import chat_manager 

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

@router.websocket("/requests/{request_id}")
async def chat_websocket(
    websocket: WebSocket,
    request_id: int,
    ticket: str = Query(..., min_length=20),
    db: Session = Depends(get_db),
):
    try: 
       current_user = verify_and_consume_chat_ticket(
           db=db,
           request_id=request_id,
           ticket=ticket,
       )
    except Exception:
        await websocket.close(
            code=1008,
            reason="Unauthorized chat connection"
        )
        return
# added after creation of chat manager
    await chat_manager.connect(
        request_id=request_id,
        user_id=current_user.id,
        wabsocket=websocket
    )

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "request_id": request_id,
                "user_id": current_user.id
            }
        )

        while True:
            raw_message = await websocket.receive_json()

            try: 
                message_data = ChatMessageCreate.model_validate(
                    raw_message
                )
            except ValidationError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Invalid chat message",
                    }
                )   
                continue

            saved_message = create_chat_message(
                db=db,
                request_id=request_id,
                current_user=current_user,
                message_data=message_data,
            )

            message_payload = ChatMessageResponse.model_validate(
                saved_message
            ).model_dump(mode="json")

            await chat_manager.broadcast(
                request_id=request_id,
                message={
                    "type": "message",
                    "message": message_payload,
                },
            )

    except WebSocketDisconnect:
        pass

    finally:
        chat_manager.disconnect(
            request_id=request_id,
            user_id=current_user.id,
            websocket=websocket,
        )    

"""
What this endpoint currently does: 
Receive ticket
  -> Verify ticket
  -> Consume ticket
  -> Validate user
  -> Validate request
  -> Validate chat authorization
  -> Accept WebSocket
  -> Send connected event
  This is the secure connection stage. It does not send chat messages yet.
  Message persistence and broadcasting come next with the connection manager.
"""
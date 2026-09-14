from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ChatMessageCreate(BaseModel):
    client_message_id: str = Field(..., min_length=1, max_length=100)
    message_text: str = Field(..., min_length=1, max_length=2000)

    model_config = ConfigDict(from_attributes=True)


class ChatMessageResponse(BaseModel):
    id: int
    request_id: int
    sender_user_id: int
    message_text: str
    client_message_id: str
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
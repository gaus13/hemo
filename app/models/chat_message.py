from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint(
            "char_length(message_text) BETWEEN 1 AND 2000",
            name="ck_chat_messages_message_text_length",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(
        Integer,
        ForeignKey("blood_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    message_text = Column(Text, nullable=False)
    client_message_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    read_at = Column(DateTime, nullable=True)

    request = relationship("BloodRequest", back_populates="chat_messages")
    sender = relationship("User", back_populates="chat_messages")

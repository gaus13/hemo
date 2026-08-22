from sqlalchemy import Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    # is_active = Column(Boolean, default=True)
    is_active = Column(
        Boolean, default=True, server_default=text("true"), nullable=False
    )
    created_at = Column(DateTime, server_default=func.now())

    donor_profile = relationship("DonorProfile", back_populates="user", uselist=False)

    requester_profile = relationship(
        "RequesterProfile", back_populates="user", uselist=False
    )

    chat_messages = relationship(
        "ChatMessage",
        back_populates="sender",
    )

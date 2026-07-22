from sqlalchemy import DateTime, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class RequesterProfile(Base):
    __tablename__ = "requester_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )
    full_name = Column(String, nullable=False)
    phone = Column(String(15), nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    created_at = Column(DateTime, server_default= func.now())

    user = relationship(
        "User", 
        back_populates="requester_profile"
    )

    blood_requests = relationship(
    "BloodRequest",
    back_populates="requester"
)
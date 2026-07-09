from sqlalchemy import DateTime, Column, String, Integer, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import BloodGroup, RequestUrgency, RequestStatus

class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id = Column(Integer, primary_key=True, index=True)

    requester_id = Column(
        Integer,
        ForeignKey("requester_profiles.id"),
        nullable=False)
    
    blood_group = Column(Enum(BloodGroup, name="blood_group"), nullable=False)
    units_required = Column(Integer, nullable=False)
    hospital_name = Column(String, nullable=False)
    hospital_address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    urgency = Column(Enum(RequestUrgency, name="request_urgency"), nullable=False)
    required_by = Column(String, nullable=False)
    status = Column(Enum(RequestStatus, name="request_status"), nullable=False)
    created_at = Column(DateTime, server_default = func.now())

    requester = relationship(
        "RequesterProfile",
        back_populates="blood_requests"
    )

    volunteers = relationship(
    "DonorVolunteer",
    back_populates="request"
    )
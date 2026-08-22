from sqlalchemy import DateTime, Column, Integer, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import VolunteerStatus

class DonorVolunteer(Base):
    __tablename__ = "donor_volunteers"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(
        Integer,
        ForeignKey("blood_requests.id"),
        nullable=False
    )
    donor_id = Column(
        Integer,
        ForeignKey("donor_profiles.id"),
        nullable=False
    )
    status = Column(Enum(VolunteerStatus, name="volunteer_status"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    donor = relationship(
    "DonorProfile",
    back_populates="volunteers"
    )

    request = relationship(
    "BloodRequest",
    back_populates="volunteers"
    )
    

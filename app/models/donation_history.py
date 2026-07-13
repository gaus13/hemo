from sqlalchemy import DateTime, Integer, String, ForeignKey, Column, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func

class DonationHistory(Base):
    __tablename__ = "donation_history"

    id = Column(Integer, primary_key=True, index=True  )
    donor_id = Column(
        Integer,
        ForeignKey("donor_profiles.id"),
        nullable=False
        )
    
    blood_request_id = Column(
        Integer,
        ForeignKey("blood_requests.id"),
        nullable=True
    )
    hospital_name = Column(String(255), nullable=False)
    units_donated = Column(Integer, nullable=False)
    donated_at = Column(DateTime, nullable=False)
    verified_by_hospital = Column(Boolean, nullable=False, default=False)
    verification_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    donor = relationship(
        "DonorProfile",
        back_populates="donation_history"
    )

    blood_request = relationship(
        "BloodRequest",
        back_populates="donation_history"
    )
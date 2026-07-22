from sqlalchemy import DateTime, Column, String, Integer, ForeignKey, Boolean, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class DonationProof(Base):
    __tablename__ = "donation_proofs"

    id = Column(Integer, primary_key=True, index=True)

    blood_request_id = Column(
        Integer,
        ForeignKey("blood_requests.id"),
        nullable=False
    )

    donor_id = Column(
        Integer,
        ForeignKey("donor_profiles.id"),
        nullable=False
    )

    proof_file = Column(String(500), nullable=False)

    uploaded_at = Column(
    DateTime,
    server_default=func.now(),
    nullable=False
    )

    requester_confirmed = Column(
    Boolean,
    default=False,
    server_default=text("false"),
    nullable=False
    )

# Relationships
    
    blood_request = relationship(
    "BloodRequest",
    back_populates="proof"
    )

    donor = relationship(
    "DonorProfile",
    back_populates="proofs"
    )
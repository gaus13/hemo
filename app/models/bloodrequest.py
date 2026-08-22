from sqlalchemy import DateTime, Column, String, Integer, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import BloodGroup, RequestUrgency, RequestStatus, RelationshipType
from geoalchemy2 import Geography

class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id = Column(Integer, primary_key=True, index=True)

    requester_id = Column(
        Integer,
        ForeignKey("requester_profiles.id"),
        nullable=False,
    )
# added the below section after geo-spatial decision
    location = Column(
        Geography(
            geometry_type="POINT",
            srid=4326,
            dimension=2,
            from_text="ST_GeogFromText",
        ),
        nullable=True,
    )
    
    blood_group = Column(Enum(BloodGroup, name="blood_group"), nullable=False)
    units_required = Column(Integer, nullable=False)
    hospital_name = Column(String, nullable=False)
    hospital_address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    urgency = Column(Enum(RequestUrgency, name="request_urgency"), nullable=False)
    # required_by = Column(String, nullable=False)
    required_by = Column(DateTime, nullable=False)
    
    # status = Column(Enum(RequestStatus, name="request_status"), nullable=False)
    status = Column(
        Enum(RequestStatus, name="request_status"),
        nullable=False,
        default=RequestStatus.ACTIVE
    )


    created_at = Column(DateTime, server_default = func.now())
    remarks = Column(Text, nullable=True)
    patient_name = Column(String(255), nullable=False)
    relationship_to_patient = Column(Enum(RelationshipType, name = "relationship_type"), nullable=False)

    matched_donor_id = Column(
    Integer,
    ForeignKey("donor_profiles.id"),
    nullable=True
    )


    requester = relationship(
        "RequesterProfile",
        back_populates="blood_requests"
    )

    volunteers = relationship(
    "DonorVolunteer",
    back_populates="request"
    )

    donation_history = relationship(
    "DonationHistory",
    back_populates="blood_request"
    )

# from donation proof table
    proof = relationship(
    "DonationProof",
    back_populates="blood_request",
    uselist=False
    )
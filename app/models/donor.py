from sqlalchemy import DateTime, String, Boolean, Integer, Column, ForeignKey, Date, Enum
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.enums import BloodGroup

class DonorProfile(Base):
    __tablename__ = "donor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id"),
        unique=True,
        nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String(15), nullable=False)
    blood_group = Column(Enum(BloodGroup, name="blood_group"), nullable=False)
    gender = Column(String, nullable= False)
    date_of_birth = Column(Date, nullable=False)
    weight = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    last_donation_date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # back_populates must match the attribute name, not the class name 
    user = relationship("User", back_populates="donor_profile")

    volunteers = relationship(
    "DonorVolunteer",
    back_populates="donor"
    )
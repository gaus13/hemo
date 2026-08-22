from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from app.models.enums import BloodGroup


class DonorProfileCreate(BaseModel):
    full_name: str
    phone: str
    blood_group: BloodGroup
    gender: str
    date_of_birth: date
    weight: int
    city: str
    state: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
"""we have not mentioned fiels like created_at: datetime, is_available: bool
Because the client should not control them, server owns these values."""

class DonorProfileResponse(BaseModel):
    """This is returned to the frontend.So now we do include database-generated fields. such as is_available, created_at"""
    id:int
    full_name: str
    phone: str
    blood_group: BloodGroup
    gender: str
    date_of_birth: date
    weight: int
    city: str
    state: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_available: bool
    created_at: datetime


    model_config = ConfigDict(
        from_attributes=True
    )

# for patch/update request schema every option become optional bcs user have the choice to update only the required fields
class DonorProfileUpdate(BaseModel):
    
    full_name: Optional[str] = None
    phone: Optional[str] = None
    blood_group: Optional[BloodGroup] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    weight: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_available: Optional[bool] = None

from pydantic import BaseModel
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
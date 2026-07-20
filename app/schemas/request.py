from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional


class RequesterProfileCreate(BaseModel):
    full_name: str
    phone: str
    city: str
    state: str

class RequesterProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    phone: str
    city: str
    state: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RequesterProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None    
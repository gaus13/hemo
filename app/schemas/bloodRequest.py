from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from app.models.enums import BloodGroup, RequestUrgency, RequestStatus

class BloodRequestCreate(BaseModel):

    """Thse belong to the backend, the frontend should not receive this data-> requester_id, created_at, status"""
    blood_group: BloodGroup
    units_required: int
    hospital_name: str
    hospital_address: str
    city: str
    urgency: RequestUrgency
    required_by: datetime
    remarks: Optional[str] = None

class BloodRequestResponse(BaseModel):

    id: int
    requester_id: int
    blood_group: BloodGroup
    units_required: int
    hospital_name: str
    hospital_address: str
    city: str
    urgency: RequestUrgency
    required_by: datetime
    remarks: Optional[str]
    status: RequestStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

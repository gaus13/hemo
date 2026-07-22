from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from app.models.enums import BloodGroup, RequestUrgency, RequestStatus, RelationshipType

class BloodRequestCreate(BaseModel):

    """Thse belong to the backend, the frontend should not receive this data-> requester_id, created_at, status"""
    blood_group: BloodGroup
    units_required: int
    hospital_name: str
    hospital_address: str
    city: str
    urgency: RequestUrgency
    required_by: datetime
    patient_name: str
    relationship_to_patient: RelationshipType
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
    patient_name: str
    relationship_to_patient: RelationshipType

    model_config = ConfigDict(
        from_attributes=True
    )

class BloodRequestUpdate(BaseModel):
    blood_group: Optional[BloodGroup] = None
    units_required: Optional[int] = None
    hospital_name: Optional[str] = None
    hospital_address: Optional[str] = None
    city: Optional[str] = None
    urgency: Optional[RequestUrgency] = None
    required_by: Optional[datetime] = None
    patient_name: Optional[str] = None
    relationship_to_patient: Optional[RelationshipType] = None
    remarks: Optional[str] = None
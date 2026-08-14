from pydantic import BaseModel
from app.models.enums import BloodGroup

class DonorMatchResponse(BaseModel):
    donor_id: int
    full_name: str
    blood_group: BloodGroup
    city: str
    state: str
    distance_km: float

    

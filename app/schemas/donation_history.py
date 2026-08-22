from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DonationHistoryResponse(BaseModel):
    id: int
    donor_id: int
    blood_request_id: Optional[int] = None
    hospital_name: str
    units_donated: int
    donated_at: datetime
    verified_by_hospital: bool
    verification_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
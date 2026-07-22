from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.enums import VolunteerStatus


class VolunteerResponse(BaseModel):
    id: int
    request_id: int
    donor_id: int
    status: VolunteerStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DonationProofUpload(BaseModel):
    proof_file: str

class DonationResponse(BaseModel):
    id: int
    blood_request_id: int
    donor_id: int
    proof_file: str
    requester_confirmed: bool
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VerificationResponse(BaseModel):
    message: str
    request_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.donation_proof import (
    DonationProofUpload,
    DonationProofResponse,
)
from app.services.donation_proof_service import upload_donation_proof


router = APIRouter(
    prefix="/donation-proof",
    tags=["Donation Proof"],
)


@router.post(
    "/{request_id}",
    response_model=DonationProofResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_donation_proof(
    request_id: int,
    request: DonationProofUpload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return upload_donation_proof(
        request_id=request_id,
        proof_file=request.proof_file,
        db=db,
        current_user=current_user,
    )
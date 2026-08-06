from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User
from app.models.donor import DonorProfile
from app.models.bloodrequest import BloodRequest
from app.models.donation_proofs import DonationProof
from app.models.enums import (
    VolunteerStatus,
    RequestStatus,
)
from app.models.donorvolunteer import DonorVolunteer


def upload_donation_proof(
        request_id: int,
        proof_file: str,
        db: Session,
        current_user: User
):
    # Find donor profile
    donor = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if donor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor Profile not found"
        )
    
     # Find blood request
    blood_request = (
        db.query(BloodRequest)
        .filter(BloodRequest.id == request_id)
        .first()
    )

    if blood_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found."
        )
    
    # Check donor was accepted
    volunteer = (
        db.query(DonorVolunteer)
        .filter(
            DonorVolunteer.request_id == request_id,
            DonorVolunteer.donor_id == donor.id,
            DonorVolunteer.status == VolunteerStatus.ACCEPTED
        )
        .first()
    )

    if volunteer is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the accepted donor."
        )

    # Check proof already uploaded
    existing = (
        db.query(DonationProof)
        .filter(DonationProof.blood_request_id == request_id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Donation proof already uploaded."
        )

    proof = DonationProof(
        blood_request_id=request_id,
        donor_id=donor.id,
        proof_file=proof_file,
    )

    db.add(proof)

    # Move request to next stage
    blood_request.status = RequestStatus.DONATION_IN_PROGRESS

    db.commit()
    db.refresh(proof)

    return proof
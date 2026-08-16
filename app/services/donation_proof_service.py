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
from app.models.requester import RequesterProfile
from app.models.donation_history import DonationHistory
from app.services.state_transition import transition_request_status

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
    # The below code removed during state transition addition and added trans_req_status
    # blood_request.status = RequestStatus.DONATION_IN_PROGRESS
    transition_request_status(
    blood_request,
    RequestStatus.DONATION_IN_PROGRESS,
)
    
    db.commit()
    db.refresh(proof)

    return proof


# this service verifies if the whole cycle is done and now time to verify the donation
def verify_donation(
        request_id: int,
        db: Session,
        current_user: User,
):

    # Find requester profile.(Only a requester should verify a donation.)
    requester = (
    db.query(RequesterProfile)
    .filter(RequesterProfile.user_id == current_user.id)
    .first()
)

    if requester is None:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Requester profile not found."
    )

    # Find the blood request. (We need the request before verifying it.)
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

    # security check
    if blood_request.requester_id != requester.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot verify someone else's request"
        )

    # Find uploaded proof.(No proof = nothing to verify.)
    proof = (
    db.query(DonationProof)
    .filter(DonationProof.blood_request_id == request_id)
    .first()
)

    if proof is None:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Donation proof not found."
    )

    # check if already verified(Prevents duplicate verification.)
    if proof.requester_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donation already verified."
        )

    #  Mark proof verified.
    proof.requester_confirmed = True

    # update request status
    # blood_request.status = RequestStatus.DONATION_VERIFIED
    transition_request_status(
    blood_request,
    RequestStatus.DONATION_VERIFIED,
)
    
    # Create donation history
    history = DonationHistory(
            donor_id= proof.donor_id,
            blood_request_id= blood_request.id,
            hospital_name= blood_request.hospital_name,
            units_donated= blood_request.units_required,
            donated_at= proof.uploaded_at,
            verified_by_hospital=False,
            verification_notes= "Verified by requester."
    )

    db.add(history)

    # Make donor unavailable.
    donor = (
        db.query(DonorProfile)
        .filter(DonorProfile.id == proof.donor_id)
        .first()
    )

    if donor is not None:
        donor.is_available = False

    db.commit()
    db.refresh(proof)

    return {
        "message": "Donation verified successfully.",
        "request_id": blood_request.id,
        "status": blood_request.status.value,
    }
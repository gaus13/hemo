from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bloodrequest import BloodRequest
from app.models.donor import DonorProfile
from app.models.enums import RequestStatus
from app.models.requester import RequesterProfile
from app.models.user import User

CHAT_ACCESS_STATUSES = {
    RequestStatus.DONOR_MATCHED,
    RequestStatus.DONATION_IN_PROGRESS,
    RequestStatus.DONATION_VERIFIED,
}


def get_authorized_chat_request(
    db: Session,
    request_id: int,
    current_user: User,
) -> BloodRequest:
    """Return a request only when the user is an active chat participant."""
    blood_request = db.query(BloodRequest).filter(BloodRequest.id == request_id).first()

    if blood_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found.",
        )

    if blood_request.status not in CHAT_ACCESS_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chat is not available for this blood request.",
        )

    is_requester = (
        db.query(RequesterProfile.id)
        .filter(
            RequesterProfile.id == blood_request.requester_id,
            RequesterProfile.user_id == current_user.id,
        )
        .first()
        is not None
    )

    is_matched_donor = (
        db.query(DonorProfile.id)
        .filter(
            DonorProfile.id == blood_request.matched_donor_id,
            DonorProfile.user_id == current_user.id,
        )
        .first()
        is not None
    )

    if not (is_requester or is_matched_donor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this chat.",
        )

    return blood_request

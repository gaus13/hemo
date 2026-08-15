from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.donor import DonorProfile
from app.models.donation_history import DonationHistory

def get_my_donation_history(
        db: Session,
        current_user: User,
):
    # Find the donor profile belonging to the logged-in user
    donor = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if donor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found.",
        )

    # Get this donor's donation history
    history = (
        db.query(DonationHistory)
        .filter(DonationHistory.donor_id == donor.id)
        .order_by(DonationHistory.donated_at.desc())
        .all()
    )

    return history
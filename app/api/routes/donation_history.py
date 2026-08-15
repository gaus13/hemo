from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user

from app.models.user import User

from app.schemas.donation_history import DonationHistoryResponse

from app.services.donation_history_service import (
    get_my_donation_history,
)

router = APIRouter(
    prefix="/donations",
    tags=["Donation History"],
)

@router.get(
    "/me",
    response_model=list[DonationHistoryResponse],
)

def get_my_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_donation_history(
        db,
        current_user,
    )
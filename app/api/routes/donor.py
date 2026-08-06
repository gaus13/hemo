from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User

from app.schemas.donor import (
    DonorProfileCreate,
    DonorProfileResponse,
    DonorProfileUpdate,
)

from app.services.donor_service import (
    create_donor_profile,
    get_my_donor_profile,
    update_donor_profile,
)

router = APIRouter(
    prefix="/donor",
    tags=["Donor"],
)


@router.post(
    "/profile",
    response_model=DonorProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    request: DonorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_donor_profile(db, current_user, request)


@router.get(
    "/profile/me",
    response_model=DonorProfileResponse,
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_donor_profile(db, current_user)


@router.patch(
    "/profile",
    response_model=DonorProfileResponse,
)
def update_profile(
    request: DonorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_donor_profile(db, current_user, request)
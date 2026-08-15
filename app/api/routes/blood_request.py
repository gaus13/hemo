from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user

from app.models.user import User

from app.schemas.bloodRequest import (
    BloodRequestCreate,
    BloodRequestResponse,
    BloodRequestUpdate,
)

from app.schemas.matching import DonorMatchResponse

from app.services.blood_request_service import (
    create_blood_request,
    get_my_blood_requests,
    update_blood_request,
    complete_blood_request
)

from app.services.matching_service import (
    find_matching_donors,
)


router = APIRouter(
    prefix="/blood-request",
    tags=["Blood Request"],
)


@router.post(
    "",
    response_model=BloodRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_request(
    request: BloodRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_blood_request(
        db,
        current_user,
        request,
    )


@router.get(
    "/me",
    response_model=list[BloodRequestResponse],
)
def get_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_blood_requests(
        db,
        current_user,
    )


@router.get(
    "/{request_id}/matches",
    response_model=list[DonorMatchResponse],
)
def get_matching_donors(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return find_matching_donors(
        db,
        current_user,
        request_id,
    )


@router.patch(
    "/{request_id}",
    response_model=BloodRequestResponse,
)
def update_request(
    request_id: int,
    request: BloodRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_blood_request(
        db,
        current_user,
        request_id,
        request,
    )


@router.patch(
    "/{request_id}/complete",
    response_model=BloodRequestResponse,
)

def complete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return complete_blood_request(
        db,
        current_user,
        request_id,
    )
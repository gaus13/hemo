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

from app.services.blood_request_service import (
    create_blood_request,
    get_my_blood_requests,
    update_blood_request,
)

router = APIRouter(
    prefix="/blood-request",
    tags=["Blood Request"],
)


@router.post(
    "",
    response_model=BloodRequestResponse,
    status_code=status.HTTP_201_CREATED
)
def create_request(
    request: BloodRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_blood_request(db, current_user, request)


@router.get(
    "/me",
    response_model=list[BloodRequestResponse]
)
def get_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_blood_requests(db, current_user)


@router.patch(
    "/{request_id}",
    response_model=BloodRequestResponse
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
        request
    )
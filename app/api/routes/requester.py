from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User

from app.schemas.request import (
    RequesterProfileCreate,
    RequesterProfileResponse,
    RequesterProfileUpdate,
)

from app.services.requester_service import (
    create_requester_profile,
    get_my_requester_profile,
    update_requester_profile,
)

router = APIRouter(
    prefix="/requester",
    tags=["Requester"]
)


@router.post(
    "/profile",
    response_model=RequesterProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    request: RequesterProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_requester_profile(db, current_user, request)


@router.get(
    "/profile/me",
    response_model=RequesterProfileResponse,
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_requester_profile(db, current_user)


@router.patch(
    "/profile",
    response_model=RequesterProfileResponse,
)
def update_profile(
    request: RequesterProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_requester_profile(db, current_user, request)
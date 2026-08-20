from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import Query

from app.database import get_db
from app.core.deps import get_current_user

from app.models.user import User
from app.models.enums import BloodGroup, RequestUrgency, RequestStatus
from app.models.bloodrequest import BloodRequest

from app.schemas.bloodRequest import (
    BloodRequestCreate,
    BloodRequestResponse,
    BloodRequestUpdate,
    BloodRequestPublicResponse
)

from app.schemas.matching import DonorMatchResponse

from app.services.blood_request_service import (
    create_blood_request,
    get_my_blood_requests,
    update_blood_request,
    complete_blood_request,
    cancel_blood_request,
    discover_blood_requests
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


@router.get(
    "/discover",
    response_model=list[BloodRequestPublicResponse],
)
def discover_request(
    blood_group: Optional[BloodGroup] = None,
    city: Optional[str] = None,
    urgency: Optional[RequestUrgency] = None,
    sort_by: str = Query(
        default="newest",
        pattern="^(newest|urgent|required_by)$",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
):
    return discover_blood_requests(
        db=db,
        blood_group=blood_group,
        city=city,
        urgency=urgency,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )



@router.get(
    "/discover/{request_id}",
    response_model=BloodRequestPublicResponse,
)
def discover_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
):
    blood_request = (
        db.query(BloodRequest)
        .filter(
            BloodRequest.id == request_id,
            BloodRequest.status == RequestStatus.ACTIVE,
        )
        .first()
    )

    if blood_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active blood request not found.",
        )

    return blood_request



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


@router.patch(
    "/{request_id}/cancel",
    response_model=BloodRequestResponse,
)
def cancel_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cancel_blood_request(
        db,
        current_user,
        request_id,
    )
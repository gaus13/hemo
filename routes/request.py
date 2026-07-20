from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.requester import RequesterProfile
from app.schemas.request import RequesterProfileCreate, RequesterProfileResponse, RequesterProfileUpdate

router = APIRouter(
    prefix="/requester",
    tags=["Requester"]
)

@router.post(
    # This is what your API sends back to the frontend, via response_model=DonorProfileResponse
    "/profile",
    response_model = RequesterProfileResponse,
    status_code= status.HTTP_201_CREATED
)

def create_requester_profile(
    request: RequesterProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    existing_requester_profile = (
        db.query(RequesterProfile)
        .filter(RequesterProfile.user_id == current_user.id)
        .first()
    )

    if existing_requester_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Requester profile already exists."
        )
    
    requester_profile = RequesterProfile(
        # Create a new requester profile if the profile doesnt exists
        user_id=current_user.id,
        full_name=request.full_name,
        phone=request.phone,
        city=request.city,
        state=request.state,
        # the frontend do not sent created at so no created_at logic
    )

    # Save to database
    try:
        db.add(requester_profile)
        db.commit()
        db.refresh(requester_profile)
    except Exception:
        db.rollback()
        raise

    return requester_profile


@router.get(
    "/profile/me",
    response_model=RequesterProfileResponse
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requester_profile = (
        db.query(RequesterProfile)
        .filter(RequesterProfile.user_id == current_user.id)
        .first()
    )

    if requester_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester profile not found."
        )

    return requester_profile


@router.patch(
    "/profile",
    response_model=RequesterProfileResponse
)
def update_profile(
    request: RequesterProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requester_profile = (
        db.query(RequesterProfile)
        .filter(RequesterProfile.user_id == current_user.id)
        .first()
    )

    if requester_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester profile not found."
        )

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(requester_profile, field, value)

    db.commit()
    db.refresh(requester_profile)

    return requester_profile
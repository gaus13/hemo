from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.donor import DonorProfile
from app.schemas.donor import DonorProfileCreate, DonorProfileResponse,DonorProfileUpdate

# create router
router = APIRouter(
    prefix="/donor",
    tags=["Donor"]
)

@router.post(
    "/profile",
    response_model=DonorProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_profile(
    request: DonorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if the logged-in user already has a donor profile
    existing_profile = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Donor profile already exists."
        )

    # Create a new donor profile
    donor_profile = DonorProfile(
        user_id=current_user.id,
        full_name=request.full_name,
        phone=request.phone,
        blood_group=request.blood_group,
        gender=request.gender,
        date_of_birth=request.date_of_birth,
        weight=request.weight,
        city=request.city,
        state=request.state,
        latitude=request.latitude,
        longitude=request.longitude
    )

    # Save to database
    try:
        db.add(donor_profile)
        db.commit()
        db.refresh(donor_profile)
    except Exception:
        db.rollback()
        raise

    return donor_profile


# Why are we returning donor_profile and not DonorProfileResponse? (get the answer yourself)

@router.get(
    "/profile/me",
     response_model=DonorProfileResponse
)

def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    """ We already know the user exists. Why? Because get_current_user() already did this, 
    so now we check if donor profile exists """
   
   #  Query DB 
    donor_profile = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if donor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found"
        )
    
    return donor_profile

@router.patch(
    "/profile",
    response_model=DonorProfileResponse,
    status_code=status.HTTP_200_OK
)

def update_profile(
    request: DonorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    donor_profile = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if donor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor Profile not found"
        )
    
     # Update only the fields sent by the client
    update_data = request.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(donor_profile, field, value)

    # save changes to db
    db.commit()
    db.refresh(donor_profile)

    return donor_profile
     
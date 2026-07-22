from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.donor import DonorProfile

from app.schemas.donor import (
    DonorProfileCreate,
    DonorProfileUpdate,
)


def create_donor_profile(
    db: Session,
    current_user: User,
    request: DonorProfileCreate,
):
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
        longitude=request.longitude,
    )

    try:
        db.add(donor_profile)
        db.commit()
        db.refresh(donor_profile)
    except Exception:
        db.rollback()
        raise

    return donor_profile


def get_my_donor_profile(
    db: Session,
    current_user: User,
):
    donor_profile = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if donor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found."
        )

    return donor_profile


def update_donor_profile(
    db: Session,
    current_user: User,
    request: DonorProfileUpdate,
):
    donor_profile = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if donor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found."
        )

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(donor_profile, field, value)

    db.commit()
    db.refresh(donor_profile)

    return donor_profile
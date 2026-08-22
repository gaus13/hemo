from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from app.models.user import User
from app.models.donor import DonorProfile
from app.schemas.donor import (
    DonorProfileCreate,
    DonorProfileUpdate,
)
from app.services.donor_mapper import donor_to_response


def create_donor_profile(
    db: Session,
    current_user: User,
    request: DonorProfileCreate,
):
    # Check if donor profile already exists
    existing_profile = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Donor profile already exists.",
        )

    # Convert latitude + longitude into a PostGIS POINT
    location = None

    if request.latitude is not None and request.longitude is not None:
        location = WKTElement(
            f"POINT({request.longitude} {request.latitude})",
            srid=4326,
        )

    # Create donor profile
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
        location=location,
    )

    # Save to database
    try:
        db.add(donor_profile)
        db.commit()
        db.refresh(donor_profile)
    except Exception:
        db.rollback()
        raise

    # Convert DB model → API response
    return donor_to_response(donor_profile)


def get_my_donor_profile(
    db: Session,
    current_user: User,
):
    # Find current user's donor profile
    donor_profile = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if donor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found.",
        )

    # Convert DB model → API response
    return donor_to_response(donor_profile)


def update_donor_profile(
    db: Session,
    current_user: User,
    request: DonorProfileUpdate,
):
    # Find current user's donor profile
    donor_profile = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if donor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found.",
        )

    # Get only fields actually sent by the client
    update_data = request.model_dump(exclude_unset=True)

    # Remove coordinates from normal update.
    # They need special handling because they become a PostGIS POINT.
    latitude = update_data.pop("latitude", None)
    longitude = update_data.pop("longitude", None)

    # Update normal fields
    for field, value in update_data.items():
        setattr(donor_profile, field, value)

    # Update location only when both coordinates are provided
    if latitude is not None and longitude is not None:
        donor_profile.location = WKTElement(
            f"POINT({longitude} {latitude})",
            srid=4326,
        )

    # Save changes
    try:
        db.commit()
        db.refresh(donor_profile)
    except Exception:
        db.rollback()
        raise

    # Convert DB model → API response
    return donor_to_response(donor_profile)
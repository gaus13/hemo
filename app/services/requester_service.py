from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.requester import RequesterProfile

from app.schemas.request import (
    RequesterProfileCreate,
    RequesterProfileUpdate,
)


def create_requester_profile(
    db: Session,
    current_user: User,
    request: RequesterProfileCreate,
):
    existing_profile = (
        db.query(RequesterProfile)
        .filter(RequesterProfile.user_id == current_user.id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Requester profile already exists."
        )

    requester_profile = RequesterProfile(
        user_id=current_user.id,
        full_name=request.full_name,
        phone=request.phone,
        city=request.city,
        state=request.state,
    )

    try:
        db.add(requester_profile)
        db.commit()
        db.refresh(requester_profile)
    except Exception:
        db.rollback()
        raise

    return requester_profile


def get_my_requester_profile(
    db: Session,
    current_user: User,
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


def update_requester_profile(
    db: Session,
    current_user: User,
    request: RequesterProfileUpdate,
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
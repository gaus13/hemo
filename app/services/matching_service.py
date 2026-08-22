from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.requester import RequesterProfile
from app.models.donor import DonorProfile
from app.models.bloodrequest import BloodRequest
from app.models.enums import RequestStatus

from app.services.blood_compatibility import (
    get_compatible_blood_groups,
)
from app.services.donor_mapper import donor_match_to_response

"""we updated the service, bcs The service accepted current_user, but didn't actually use it to verify ownership.
   That's a security/authorization problem."""

def find_matching_donors(
    db: Session,
    current_user: User,
    request_id: int,
):
    # ---------------------------------------------------------
    # 1. Find the requester's profile
    # ---------------------------------------------------------
    requester = (
        db.query(RequesterProfile)
        .filter(RequesterProfile.user_id == current_user.id)
        .first()
    )

    if requester is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester profile not found.",
        )

    # ---------------------------------------------------------
    # 2. Find the blood request belonging to this requester
    # ---------------------------------------------------------
    blood_request = (
        db.query(BloodRequest)
        .filter(
            BloodRequest.id == request_id,
            BloodRequest.requester_id == requester.id,
        )
        .first()
    )

    if blood_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found.",
        )

    # ---------------------------------------------------------
    # 3. Only active requests can find donors
    # ---------------------------------------------------------
    if blood_request.status != RequestStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active requests can find donors.",
        )

    # ---------------------------------------------------------
    # 4. Request must have a geographic location
    # ---------------------------------------------------------
    if blood_request.location is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blood request location is not available.",
        )

    # ---------------------------------------------------------
    # 5. Get compatible donor blood groups
    # ---------------------------------------------------------
    compatible_groups = get_compatible_blood_groups(
        blood_request.blood_group
    )

    # ---------------------------------------------------------
    # 6. Calculate distance using PostGIS
    #
    # ST_Distance on Geography returns meters.
    # Divide by 1000 -> kilometers.
    # ---------------------------------------------------------
    distance_km = (
        func.ST_Distance(
            DonorProfile.location,
            blood_request.location,
        )
        / 1000
    ).label("distance_km")

    # ---------------------------------------------------------
    # 7. Find available compatible donors with location
    # ---------------------------------------------------------
    matches = (
        db.query(
            DonorProfile,
            distance_km,
        )
        .filter(
            DonorProfile.blood_group.in_(compatible_groups),
            DonorProfile.is_available.is_(True),
            DonorProfile.location.is_not(None),
        )
        .order_by(distance_km.asc())
        .all()
    )

    # ---------------------------------------------------------
    # 8. Convert database results into API responses
    # ---------------------------------------------------------
    return [
        donor_match_to_response(
            donor,
            distance_km,
        )
        for donor, distance_km in matches
    ]
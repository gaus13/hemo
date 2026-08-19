from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from geoalchemy2.elements import WKTElement

from app.services.blood_request_mapper import blood_request_to_response
from app.services.state_transition import transition_request_status
from app.models.user import User
from app.models.requester import RequesterProfile
from app.models.bloodrequest import BloodRequest
from app.models.donor import DonorProfile

from app.schemas.bloodRequest import (
    BloodRequestCreate,
    BloodRequestUpdate,
)

from app.models.enums import RequestStatus

from app.services.blood_request_mapper import blood_request_to_response
from app.services.notification_events import publish_notification


def create_blood_request(
    db: Session,
    current_user: User,
    request: BloodRequestCreate,
):

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

    active_request = (
        db.query(BloodRequest)
        .filter(BloodRequest.requester_id == requester.id)
        .filter(BloodRequest.status == RequestStatus.ACTIVE)
        .first()
    )

    if active_request:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an active blood request.",
        )

    # Convert latitude + longitude into PostGIS POINT
    location = None

    if request.latitude is not None and request.longitude is not None:
        location = WKTElement(
            f"POINT({request.longitude} {request.latitude})",
            srid=4326,
        )

    # Reject incomplete coordinates
    elif request.latitude is not None or request.longitude is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both latitude and longitude must be provided.",
        )

    blood_request = BloodRequest(
        requester_id=requester.id,
        patient_name=request.patient_name,
        relationship_to_patient=request.relationship_to_patient,
        blood_group=request.blood_group,
        units_required=request.units_required,
        hospital_name=request.hospital_name,
        hospital_address=request.hospital_address,
        city=request.city,
        urgency=request.urgency,
        required_by=request.required_by,
        remarks=request.remarks,
        location=location,
    )

    try:
        db.add(blood_request)
        db.commit()
        db.refresh(blood_request)

    except Exception:
        db.rollback()
        raise

    publish_notification(
        current_user.id,
        "blood_request.created",
        "Blood request created",
        "Your blood request has been created successfully.",
        request_id=blood_request.id,
        status=blood_request.status.value,
    )

    return blood_request_to_response(blood_request)


def get_my_blood_requests(
    db: Session,
    current_user: User,
):

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

    requests = (
        db.query(BloodRequest)
        .filter(BloodRequest.requester_id == requester.id)
        .order_by(BloodRequest.created_at.desc())
        .all()
    )

    return [blood_request_to_response(blood_request) for blood_request in requests]


def update_blood_request(
    db: Session,
    current_user: User,
    request_id: int,
    request: BloodRequestUpdate,
):

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

    blood_request = (
        db.query(BloodRequest)
        .filter(BloodRequest.id == request_id)
        .filter(BloodRequest.requester_id == requester.id)
        .first()
    )

    if blood_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found.",
        )

    if blood_request.status != RequestStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active requests can be updated.",
        )

    update_data = request.model_dump(exclude_unset=True)

    # Remove coordinates from normal setattr().
    # They need to be converted into a PostGIS POINT.
    latitude = update_data.pop("latitude", None)
    longitude = update_data.pop("longitude", None)

    # Update normal fields
    for field, value in update_data.items():
        setattr(blood_request, field, value)

    # Coordinates were supplied
    if latitude is not None or longitude is not None:

        # Both must be supplied together
        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both latitude and longitude must be provided.",
            )

        blood_request.location = WKTElement(
            f"POINT({longitude} {latitude})",
            srid=4326,
        )

    try:
        db.commit()
        db.refresh(blood_request)

    except Exception:
        db.rollback()
        raise

    publish_notification(
        current_user.id,
        "blood_request.updated",
        "Blood request updated",
        "Your blood request details were updated.",
        request_id=blood_request.id,
    )

    return blood_request_to_response(blood_request)


def cancel_blood_request(
    db: Session,
    current_user: User,
    request_id: int,
):
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

    # A request cannot be cancelled after donation has started.
    if blood_request.status not in (
        RequestStatus.ACTIVE,
        RequestStatus.DONOR_MATCHED,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This blood request can no longer be cancelled.",
        )

    # blood_request.status = RequestStatus.CANCELLED
    transition_request_status(
        blood_request,
        RequestStatus.CANCELLED,
    )

    try:
        db.commit()
        db.refresh(blood_request)
    except Exception:
        db.rollback()
        raise

    publish_notification(
        current_user.id,
        "blood_request.cancelled",
        "Blood request cancelled",
        "Your blood request has been cancelled.",
        request_id=blood_request.id,
    )

    return blood_request_to_response(blood_request)


def complete_blood_request(
    db: Session,
    current_user: User,
    request_id: int,
):
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

    if blood_request.status != RequestStatus.DONATION_VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only verified donations can be completed.",
        )

    # blood_request.status = RequestStatus.COMPLETED
    transition_request_status(
        blood_request,
        RequestStatus.COMPLETED,
    )

    try:
        db.commit()
        db.refresh(blood_request)
    except Exception:
        db.rollback()
        raise

    if blood_request.matched_donor_id is not None:
        donor = (
            db.query(DonorProfile)
            .filter(DonorProfile.id == blood_request.matched_donor_id)
            .first()
        )
        if donor is not None:
            publish_notification(
                donor.user_id,
                "blood_request.completed",
                "Donation completed",
                "The blood request you helped with is now complete.",
                request_id=blood_request.id,
            )

    publish_notification(
        current_user.id,
        "blood_request.completed",
        "Blood request completed",
        "Your blood request has been completed.",
        request_id=blood_request.id,
    )
    # Return change to this long mapper func, Otherwise /complete can return the raw location Geography object instead of the API representation your frontend expects.
    return blood_request_to_response(blood_request)

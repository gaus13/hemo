from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.requester import RequesterProfile
from app.models.bloodrequest import BloodRequest

from app.schemas.bloodRequest import (
    BloodRequestCreate,
    BloodRequestUpdate,
)

from app.models.enums import RequestStatus

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
            detail="Requester profile not found."
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
            detail="You already have an active blood request."
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
    )

    try:
        db.add(blood_request)
        db.commit()
        db.refresh(blood_request)

    except Exception:
        db.rollback()
        raise

    return blood_request

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
            detail="Requester profile not found."
        )

    requests = (
        db.query(BloodRequest)
        .filter(BloodRequest.requester_id == requester.id)
        .order_by(BloodRequest.created_at.desc())
        .all()
    )

    return requests

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
            detail="Requester profile not found."
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
            detail="Blood request not found."
        )

    if blood_request.status != RequestStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active requests can be updated."
        )

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(blood_request, field, value)

    db.commit()
    db.refresh(blood_request)

    return blood_request
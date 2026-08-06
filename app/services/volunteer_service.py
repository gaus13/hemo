from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import User
from app.models.donor import DonorProfile
from app.models.requester import RequesterProfile
from app.models.bloodrequest import BloodRequest
from app.models.donorvolunteer import DonorVolunteer
from app.models.enums import RequestStatus, VolunteerStatus

def volunteer_for_request(
        request_id: int,
        db: Session,
        current_user: User
):
    # Find donor profile by query the db
    donor = (
        db.query(DonorProfile)
        .filter(DonorProfile.user_id == current_user.id)
        .first()
    )

    if donor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor Profile not found"
        )
    
    # Find blood request that if it exists in the db
    blood_request = (
        db.query(BloodRequest)
        .filter(BloodRequest.id == request_id)
        .first()
    )

    if blood_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found"
        )
    
    # Check request status
    if blood_request.status != RequestStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request is no longer accepting volunteers"
        )
    
    # Check duplicate volunteer(The same donor volunteering for the same request again.)
    duplicate_volunteer = (
        db.query(DonorVolunteer)
        .filter(DonorVolunteer.request_id == request_id, DonorVolunteer.donor_id == donor.id)
        .first()
    )

    if duplicate_volunteer:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="You have already volunteered for this request."
    )
    
    volunteer = DonorVolunteer(
        request_id=request_id,
        donor_id=donor.id,
        status=VolunteerStatus.PENDING,
    )

    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)

    return volunteer

def accept_volunteer(
        # Which volunteer did the requester click Accept on?
        volunteer_id: int,
        db: Session,
        current_user: User
):
    
    # Get the requester profile
    requester = (
        db.query(RequesterProfile)
        .filter(RequesterProfile.user_id == current_user.id)
        .first()
    )

    if requester is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester profile not found"
        )


    # Find the volunteer
    volunteer = (
    db.query(DonorVolunteer)
    .filter(DonorVolunteer.id == volunteer_id)
    .first()
    )

    if volunteer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )

    if volunteer.status != VolunteerStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )


    # Get the blood request
    blood_request = (
    db.query(BloodRequest)
    .filter(BloodRequest.id == volunteer.request_id)
    .first()
    )

    if blood_request is None:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Blood request not found."
    )


    # Security Check, Does this blood request belong to the logged-in requester?
    if blood_request.requester_id != requester.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Request"
        )


    # Is the request still ACTIVE?
    if blood_request.status != RequestStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request is no longer accepting volunteers"
        )
    
    # Accept the selected volunteer
    volunteer.status = VolunteerStatus.ACCEPTED


    # Reject all other volunteers for the same blood request
    other_volunteers = (
        db.query(DonorVolunteer)
        .filter(
            # "Give me only the volunteers who belong to this blood request."
            DonorVolunteer.request_id == blood_request.id,
            # "But don't include the volunteer I already accepted."
            DonorVolunteer.id != volunteer.id
        )
        .all()
    )

    for other in other_volunteers:
        other.status = VolunteerStatus.REJECTED


    # Update the blood request
    blood_request.matched_donor_id = volunteer.donor_id
    blood_request.status = RequestStatus.DONOR_MATCHED


    # Save all changes
    db.commit()

    db.refresh(volunteer)

    return volunteer
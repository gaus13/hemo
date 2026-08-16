from fastapi import HTTPException, status

from app.models.bloodrequest import BloodRequest
from app.models.enums import RequestStatus


ALLOWED_TRANSITIONS = {
    RequestStatus.ACTIVE: {
        RequestStatus.DONOR_MATCHED,
        RequestStatus.CANCELLED,
    },

    RequestStatus.DONOR_MATCHED: {
        RequestStatus.ACTIVE,
        RequestStatus.DONATION_IN_PROGRESS,
        RequestStatus.CANCELLED,
    },

    RequestStatus.DONATION_IN_PROGRESS: {
        RequestStatus.DONATION_VERIFIED,
    },

    RequestStatus.DONATION_VERIFIED: {
        RequestStatus.COMPLETED,
    },
#Used set() bcs COMPLETED → anything is invalid, There are zero valid next states.
    RequestStatus.COMPLETED: set(),

    RequestStatus.CANCELLED: set(),
}

"""
I intentionally included:

DONOR_MATCHED → CANCELLED
because the requester can cancel a matched request, which we just implemented.

And:

DONOR_MATCHED → ACTIVE
because the accepted donor can cancel, after which another donor can volunteer.

But I did not include:
DONATION_IN_PROGRESS → CANCELLED

because we've decided that once the actual donation process has started, normal cancellation should no longer be allowed."""


def transition_request_status(
    blood_request: BloodRequest,
    new_status: RequestStatus,
):
    current_status = blood_request.status

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{current_status.value} -> {new_status.value}"
            ),
        )

    blood_request.status = new_status

    return blood_request
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.volunteer import VolunteerResponse
from app.services.volunteer_service import volunteer_for_request

router = APIRouter(
    prefix="/volunteer",
    tags=["Volunteer"]
)

@router.post(
    "/{request_id}",
    response_model = VolunteerResponse,
    status_code=status.HTTP_201_CREATED
)

def create_volunteer(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return volunteer_for_request(
        request_id=request_id,
        db=db,
        current_user=current_user
    )
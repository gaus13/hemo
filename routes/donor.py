from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.donor import DonorProfile
from app.schemas.donor import DonorProfileCreate, DonorProfileResponse

# create router
router = APIRouter(
    prefix="/donor",
    tags=["Donor"]
)

@router.post("/profile", response_model= DonorProfileCreate, status_code=status.HTTP_201_CREATED)

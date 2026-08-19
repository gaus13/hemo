from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.donor import router as donor_router
from app.api.routes.requester import router as requester_router
from app.api.routes.blood_request import router as blood_request_router
from app.api.routes.volunteer import router as volunteer_router
from app.api.routes.donation_proof import router as donation_proof_router
from app.api.routes.donation_history import router as donation_history_router
from app.api.routes.notification import router as notification_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(donor_router)
api_router.include_router(requester_router)
api_router.include_router(blood_request_router)
api_router.include_router(volunteer_router)
api_router.include_router(donation_proof_router)
api_router.include_router(donation_history_router)
api_router.include_router(notification_router)

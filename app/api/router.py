from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.donor import router as donor_router
from app.api.routes.requester import router as requester_router
from app.api.routes.blood_request import router as blood_request_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(donor_router)
api_router.include_router(requester_router)
api_router.include_router(blood_request_router)
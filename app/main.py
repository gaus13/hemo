from fastapi import FastAPI
from app.config import settings

from app.api import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

app.include_router(api_router)

@app.get("/")
def root():
    return{
        "message": "Blood Donation API is running"
    }

@app.get("/health")
def health():
    return{
        "status": "healthy"
    }
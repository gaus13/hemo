from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

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
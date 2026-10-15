import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import api_router
from app.config import settings
from app.core.redis_async import redis_async_client
from app.services.chat_pubsub import run_chat_pubsub_listener


@asynccontextmanager
async def lifespan(app: FastAPI):
    pubsub_task = asyncio.create_task(run_chat_pubsub_listener())

    try:
        yield

    finally:
        pubsub_task.cancel()
        await asyncio.gather(
            pubsub_task,
            return_exceptions=True,
        )
        await redis_async_client.aclose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Blood Donation API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


"WHAT IS THIS LIFESPAN AND WHY IS IT NEEDED????"

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import api_router
from app.config import settings
from app.core.redis_async import redis_async_client
from app.services.chat_pubsub import run_chat_pubsub_listener
from app.services.chat_connection_manager import chat_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    pubsub_ready = asyncio.Event()
    pubsub_task = asyncio.create_task(run_chat_pubsub_listener(pubsub_ready))

    try:
        await asyncio.wait_for(
            pubsub_ready.wait(),
            timeout=5,
        )
        yield

    finally:
        pubsub_task.cancel()

        await asyncio.gather(
            pubsub_task,
            return_exceptions=True,
        )
        # This prevents the server from abandoning active WebSocket connections during deployment or restart.
        await chat_manager.close_all()

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

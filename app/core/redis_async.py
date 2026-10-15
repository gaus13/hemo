"""Why a second client??
Normal Redis client:
Used by synchronous HTTP services

Async Redis client:
Used by async WebSocket and Pub/Sub code.
Using the synchronous client inside async WebSocket code can block the event loop."""


from redis.asyncio import Redis
from app.config import settings

redis_async_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses= True,
)
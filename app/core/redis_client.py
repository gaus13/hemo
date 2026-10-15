import redis

from app.config import settings

# ye redis ko start kar rha port 6379 pe
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)
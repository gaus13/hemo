import redis

# ye redis ko start kar rha port 6379 pe
redis_client = redis.Redis(
    host = "localhost",
    port=6379,
    decode_responses=True,
)
# This file acts as a redis publisher, Its job is to send an event to Redis.
import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

from redis.exceptions import RedisError

from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


def publish_event(channel: str, event: dict) -> bool:
    """Publish a JSON event after the database transaction has succeeded.
    channel: the Redis topic
    event: the message being sent"""
    message = json.dumps(
        {
            "event_id": str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            **event,
        }
    )

    try:
        redis_client.publish(channel, message)
    except RedisError:
        # Redis is a notification aid, so it must not undo a saved action.
        logger.exception("Could not publish notification event to Redis")
        return False

    return True

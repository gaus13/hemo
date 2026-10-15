import asyncio
import json
import logging

from redis.exceptions import RedisError

from app.core.redis_async import redis_async_client
from app.services.chat_connection_manager import chat_manager

logger = logging.getLogger(__name__)

CHAT_CHANNEL_PATTERN = "chat:request:*"


def get_chat_channel(request_id: int) -> str:
    return f"chat:request:{request_id}"


async def publish_chat_event(
    request_id: int,
    event: dict,
) -> bool:
    try:
        await redis_async_client.publish(
            get_chat_channel(request_id), json.dumps(event)
        )
    except RedisError:
        logger.exception(
            "Could not publish chat event",
            extra={"request_id": request_id},
        )
        return False

    return True


async def run_chat_pubsub_listener() -> None:
    while True:
        pubsub = redis_async_client.pubsub()

        try:
            await pubsub.psubscribe(CHAT_CHANNEL_PATTERN)

            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )

                if message is None:
                    await asyncio.sleep(0.01)
                    continue

                if message["type"] != "pmessage":
                    continue

                event = json.loads(message["data"])
                request_id = int(event["request_id"])

                await chat_manager.broadcast(
                    request_id=request_id,
                    message=event,
                )

        except asyncio.CancelledError:
            raise

        except (RedisError, json.JSONDecodeError, KeyError, ValueError):
            logger.exception("Chat Pub/Sub listener failed")
            await asyncio.sleep(1)

        finally:
            await pubsub.aclose()

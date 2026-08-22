import json
import logging

from app.core.redis_client import redis_client
from app.database import SessionLocal
from app.services.notification_service import handle_notification_event

CHANNEL = "blood_request.events"
logger = logging.getLogger(__name__)


def start_worker():
    # Creates a Pub/Sub (Publisher/Subscriber) object. This allows the script to subscribe to channels and receive broadcasts.
    pubsub = redis_client.pubsub()
    pubsub.subscribe(CHANNEL)

    print(f"Notification worker listening on: {CHANNEL}")

    for message in pubsub.listen():
        if message["type"] == "message":
            db = SessionLocal()
            try:
                event = json.loads(message["data"])
                handle_notification_event(db, event)
            except (ValueError, TypeError):
                logger.exception("Ignoring invalid notification event")
            except Exception:
                db.rollback()
                logger.exception("Could not process notification event")
            finally:
                db.close()


if __name__ == "__main__":
    start_worker()

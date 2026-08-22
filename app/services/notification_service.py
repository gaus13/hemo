import json
import logging

from sqlalchemy.orm import Session

from app.models.notification import Notification

logger = logging.getLogger(__name__)


def _send_web_push(event: dict) -> None:
    # A real web-push adapter can be connected here when browser subscriptions exist.
    logger.debug("Web Push notification ready for event %s", event["event_id"])


def _send_fcm(event: dict) -> None:
    # A real FCM adapter can be connected here when Android tokens exist.
    logger.debug("FCM notification ready for event %s", event["event_id"])


def handle_notification_event(db: Session, event: dict) -> Notification | None:
    """Store one event and fan it out to the available notification channels."""
    required_fields = (
        "event_id",
        "recipient_user_id",
        "event_type",
        "title",
        "message",
    )

    if any(field not in event for field in required_fields):
        logger.error("Ignoring incomplete notification event: %s", event)
        return None

    # Redis can deliver the same message again, so processing is idempotent.
    existing = (
        db.query(Notification)
        .filter(Notification.event_id == event["event_id"])
        .first()
    )
    if existing is not None:
        return existing

    notification = Notification(
        event_id=event["event_id"],
        recipient_user_id=event["recipient_user_id"],
        event_type=event["event_type"],
        title=event["title"],
        message=event["message"],
        payload=json.dumps(event),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    _send_web_push(event)
    _send_fcm(event)
    return notification

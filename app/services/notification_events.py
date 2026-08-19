from app.core.redis_service import publish_event

CHANNEL = "blood_request.events"


def publish_notification(
    recipient_user_id: int,
    event_type: str,
    title: str,
    message: str,
    **payload,
) -> None:
    # Send the event only after the caller has committed its database change.
    publish_event(
        CHANNEL,
        {
            "recipient_user_id": recipient_user_id,
            "event_type": event_type,
            "title": title,
            "message": message,
            "payload": payload,
        },
    )

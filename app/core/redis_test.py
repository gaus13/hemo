from app.core.redis_client import redis_client
from app.core.redis_service import publish_event

# redis_client.set("hemo_test", "hello nilo ka redis")
# value = redis_client.get("hemo_test")
# print(value)

publish_event(
    "blood_request.events",
    {
        "event": "blood_request.reactivated",
        "request_id": 123,
    },
)

print("Event published")
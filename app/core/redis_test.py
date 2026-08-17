from app.core.redis_client import redis_client

redis_client.set("hemo_test", "hello fkufn redis")

value = redis_client.get("hemo_test")
print(value)
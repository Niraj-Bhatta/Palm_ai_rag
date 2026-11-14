
from app.services.memory_service import get_redis_client

try:
    redis_client = get_redis_client()

    redis_client.ping()

    print("Redis connection successful!")

except Exception as error:
    print("Redis connection failed:", error)

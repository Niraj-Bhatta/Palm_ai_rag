
import os
import json

import redis
from dotenv import load_dotenv

load_dotenv()


def get_redis_client() -> redis.Redis:
    """Create a Redis client using environment configuration."""

    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD"),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True,
        socket_connect_timeout=10,
    )


class ConversationMemory:
    """Store and retrieve conversation history using Redis."""

    def __init__(self, client: redis.Redis) -> None:
        self.client = client

    def get_history(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """Retrieve the most recent conversation messages."""

        key = f"conversation:{conversation_id}"

        messages = self.client.lrange(key, -limit, -1)

        return [json.loads(message) for message in messages]

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None:
        """Save a user or assistant message."""

        key = f"conversation:{conversation_id}"

        message = {
            "role": role,
            "content": content,
        }

        self.client.rpush(key, json.dumps(message))

        # Automatically expire inactive conversations after 24 hours.
        self.client.expire(key, 86400)



    def get_booking_state(
        self,
        conversation_id: str,
    ) -> dict | None:
        """Retrieve pending booking information from Redis."""

        key = f"booking:{conversation_id}"

        state = self.client.get(key)

        if state is None:
            return None

        return json.loads(state)

    def save_booking_state(
        self,
        conversation_id: str,
        state: dict,
    ) -> None:
        """Save pending booking information in Redis."""

        key = f"booking:{conversation_id}"

        self.client.set(
            key,
            json.dumps(state),
            ex=86400,
        )

    def clear_booking_state(
        self,
        conversation_id: str,
    ) -> None:
        """Remove booking information after completion."""

        key = f"booking:{conversation_id}"

        self.client.delete(key)

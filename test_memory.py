
from app.services.memory_service import (
    get_redis_client,
    ConversationMemory,
)

redis_client = get_redis_client()
memory = ConversationMemory(redis_client)

conversation_id = "test-conversation-001"

# Save two messages.
memory.add_message(
    conversation_id,
    "user",
    "What leadership roles did I hold?",
)

memory.add_message(
    conversation_id,
    "assistant",
    "You were a Program Coordinator and Student Branch Ambassador.",
)

# Retrieve conversation history.
history = memory.get_history(conversation_id)

for message in history:
    print(f"{message['role']}: {message['content']}")

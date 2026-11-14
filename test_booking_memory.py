
from app.services.memory_service import (
    get_redis_client,
    ConversationMemory,
)

redis_client = get_redis_client()
memory = ConversationMemory(redis_client)

conversation_id = "booking-test-001"

state = {
    "status": "collecting",
    "candidate_name": "Niraj Bhatta",
    "email": None,
    "interview_date": None,
}

memory.save_booking_state(conversation_id, state)

result = memory.get_booking_state(conversation_id)

print("Saved booking state:")
print(result)

memory.clear_booking_state(conversation_id)

print("After clearing:")
print(memory.get_booking_state(conversation_id))

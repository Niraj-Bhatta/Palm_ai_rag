
from app.services.rag_service import is_booking_request

tests = [
    ("I want to schedule an interview.", None, True),
    ("Book my interview.", None, True),
    ("What skills are in my CV?", None, False),
    (
        "My name is Niraj Bhatta.",
        {"status": "collecting"},
        True,
    ),
    (
        "Yes, confirm it.",
        {"status": "awaiting_confirmation"},
        True,
    ),
]

for question, state, expected in tests:
    result = is_booking_request(question, state)

    print(
        f"{question} -> {result} "
        f"| Expected: {expected}"
    )

    assert result == expected

print("\nAll booking intent tests passed!")

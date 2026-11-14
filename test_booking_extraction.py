
from app.services.llm_service import get_llm_service

llm = get_llm_service()

conversation = """
User: My name is Niraj Bhatta.
User: My email is niraj@example.com.
User: I would like an interview on November 20, 2026 at 10 AM.
"""

details = llm.extract_booking_details(conversation)

print("Extracted booking details:")
print(details.model_dump())

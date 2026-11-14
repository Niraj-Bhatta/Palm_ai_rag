
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.schemas.booking import BookingCreate
from app.services.booking_service import create_booking
from app.services.llm_service import get_llm_service
from app.services.memory_service import ConversationMemory


TIMEZONE = ZoneInfo("Asia/Kathmandu")


def handle_booking_message(
    question: str,
    history: list[dict[str, str]],
    conversation_id: str,
    memory: ConversationMemory,
    db: Session,
) -> dict:
    """Handle the multi-turn interview booking conversation."""

    state = memory.get_booking_state(conversation_id) or {}

    # 1. Handle confirmation before extracting more details.
    if state.get("status") == "awaiting_confirmation":

        normalized = re.sub(
            r"[^\w\s]",
            "",
            question.lower().strip(),
        )

        affirmative = bool(
            re.fullmatch(
                r"(yes|yeah|yep|sure|confirm|confirmed|"
                r"please confirm|yes confirm( it)?|"
                r"yes save( it)?|correct)",
                normalized,
            )
        )

        negative = bool(
            re.fullmatch(
                r"(no|nope|cancel|cancel it|no cancel( it)?)",
                normalized,
            )
        )

        # Confirm booking.
        if affirmative:
            interview_date = datetime.fromisoformat(
                state["interview_date"]
            )

            if interview_date.tzinfo is None:
                interview_date = interview_date.replace(
                    tzinfo=TIMEZONE
                )

            if interview_date <= datetime.now(TIMEZONE):
                state["status"] = "collecting"
                state["interview_date"] = None

                memory.save_booking_state(
                    conversation_id,
                    state,
                )

                return {
                    "answer": (
                        "That interview date is in the past. "
                        "Please provide a future date and time."
                    ),
                    "sources": [],
                    "retrieved_count": 0,
                }

            booking_data = BookingCreate(
                conversation_id=conversation_id,
                candidate_name=state["candidate_name"],
                email=state["email"],
                interview_date=interview_date,
            )

            booking = create_booking(booking_data, db)

            memory.clear_booking_state(conversation_id)

            return {
                "answer": (
                    "Your interview booking request has been "
                    "saved successfully.\n\n"
                    f"**Name:** {booking.candidate_name}\n"
                    f"**Email:** {booking.email}\n"
                    f"**Date and time:** "
                    f"{booking.interview_date.strftime('%Y-%m-%d %H:%M')}\n\n"
                    "Your booking record is saved. The interview slot "
                    "has not been independently checked for availability."
                ),
                "sources": [],
                "retrieved_count": 0,
            }

        # Cancel booking.
        if negative:
            memory.clear_booking_state(conversation_id)

            return {
                "answer": (
                    "No problem. I've cancelled this booking process. "
                    "You can start again whenever you're ready."
                ),
                "sources": [],
                "retrieved_count": 0,
            }

        # Ask for confirmation again.
        return {
            "answer": (
                "Would you like me to save this interview booking? "
                "Please reply **yes** to confirm or **no** to cancel."
            ),
            "sources": [],
            "retrieved_count": 0,
        }

    # 2. Build extraction text using only the user's messages.
    user_messages = [
        message["content"]
        for message in history
        if message.get("role") == "user"
    ]

    conversation_text = "\n".join(user_messages + [question])

    # 3. Extract booking information using Gemini.
    extracted = get_llm_service().extract_booking_details(
        conversation_text
    )

    # 4. Merge newly extracted information with existing state.
    state["candidate_name"] = (
        extracted.candidate_name
        or state.get("candidate_name")
    )

    state["email"] = (
        str(extracted.email)
        if extracted.email
        else state.get("email")
    )

    state["interview_date"] = (
        extracted.interview_date.isoformat()
        if extracted.interview_date
        else state.get("interview_date")
    )

    state["status"] = "collecting"

    # 5. Validate that the interview date is in the future.
    if state.get("interview_date"):
        interview_date = datetime.fromisoformat(
            state["interview_date"]
        )

        if interview_date.tzinfo is None:
            interview_date = interview_date.replace(
                tzinfo=TIMEZONE
            )

        if interview_date <= datetime.now(TIMEZONE):
            state["interview_date"] = None

    # 6. Ask for missing information one field at a time.
    if not state.get("candidate_name"):
        answer = "Sure! What is your full name?"

    elif not state.get("email"):
        answer = "Thanks! What is your email address?"

    elif not state.get("interview_date"):
        answer = (
            "What date and time would you prefer for your interview? "
            "Please provide a future date and time."
        )

    else:
        # 7. All information collected: request confirmation.
        interview_date = datetime.fromisoformat(
            state["interview_date"]
        )

        if interview_date.tzinfo is None:
            interview_date = interview_date.replace(
                tzinfo=TIMEZONE
            )

        state["status"] = "awaiting_confirmation"

        answer = (
            "Please review your interview booking details:\n\n"
            f"**Name:** {state['candidate_name']}\n"
            f"**Email:** {state['email']}\n"
            f"**Date and time:** "
            f"{interview_date.strftime('%Y-%m-%d %H:%M')}\n\n"
            "Would you like me to save this booking? "
            "Reply **yes** to confirm or **no** to cancel."
        )

    # 8. Save the updated booking state in Redis.
    memory.save_booking_state(
        conversation_id,
        state,
    )

    return {
        "answer": answer,
        "sources": [],
        "retrieved_count": 0,
    }

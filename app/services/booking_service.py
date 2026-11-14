
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import Booking
from app.schemas.booking import BookingCreate


def create_booking(
    booking_data: BookingCreate,
    db: Session,
) -> Booking:
    """Create and persist an interview booking."""

    booking = Booking(
        id=str(uuid4()),
        conversation_id=booking_data.conversation_id,
        candidate_name=booking_data.candidate_name,
        email=str(booking_data.email),
        interview_date=booking_data.interview_date,
        status="confirmed",
    )

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)

        return booking

    except Exception:
        db.rollback()
        raise

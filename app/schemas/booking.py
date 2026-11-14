
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class BookingCreate(BaseModel):
    conversation_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    candidate_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    interview_date: datetime

    @field_validator("candidate_name")
    @classmethod
    def validate_candidate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Candidate name cannot be empty.")

        return value


class BookingResponse(BaseModel):
    id: str
    conversation_id: str
    candidate_name: str
    email: EmailStr
    interview_date: datetime
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BookingDetails(BaseModel):
    """Partially extracted interview booking information."""

    candidate_name: str | None = None
    email: EmailStr | None = None
    interview_date: datetime | None = None

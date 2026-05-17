from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.agents.booking.schemas import TravelIntent


class ChatRequest(BaseModel):
    conversation_id: str = Field(default="default", min_length=1)
    message: str = Field(..., min_length=1)
    user_id: str | None = None
    user_profile: dict[str, Any] | None = None
    payment_completed: bool = False
    payment_transaction_id: str | None = None
    payment_prebook_id: str | None = None

    model_config = ConfigDict(extra="forbid")


class ChatResponse(BaseModel):
    conversation_id: str
    intent: TravelIntent | None = None
    agent: str | None = None
    message: str | None = None
    next_action: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")

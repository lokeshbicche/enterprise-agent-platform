"""Validated request and response models for the production agent API."""

from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentRequest(BaseModel):
    """A user request associated with a persistent conversation thread."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=8_000)
    thread_id: UUID = Field(default_factory=uuid4)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        question = value.strip()
        if not question:
            raise ValueError("question must not be blank")
        return question


class AgentResponse(BaseModel):
    """The final answer and persistent conversation identifier."""

    thread_id: UUID
    answer: str
    workflow: str

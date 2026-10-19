"""Typed FastAPI boundary with a deterministic offline chat response."""

import json
import sys
from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=4_000)
    conversation_id: UUID = Field(default_factory=uuid4)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        message = value.strip()
        if not message:
            raise ValueError("message must not be blank")
        return message


class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str


def respond(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        conversation_id=request.conversation_id,
        answer=f"POC received: {request.message}",
    )


app = FastAPI(title="Agent Application Layer POC", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return respond(request)


def main() -> None:
    if "--demo" not in sys.argv[1:]:
        raise SystemExit("Run with --demo for a sample or use uvicorn to serve the API.")
    response = respond(ChatRequest(message="Summarize this request"))
    print(json.dumps(response.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()

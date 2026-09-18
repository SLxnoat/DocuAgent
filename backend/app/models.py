from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class StepSchema(BaseModel):
    index: int
    description: str
    action_type: str
    target_selector: str
    input_value: str
    expected_url: str
    domain_context: str
    selector_hints: list[str]

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class GenerateRequest(BaseModel):
    script: str = Field(..., min_length=10)
    target_url: HttpUrl | None = Field(default=None, description="Target staging environment URL")
    url: HttpUrl | None = Field(default=None, description="Alias for target_url")
    credentials: dict[str, Any] | None = Field(
        default=None, description="Optional login credentials (ephemeral)"
    )
    options: dict[str, Any] | None = Field(default=None, description="Generation options")

    def get_target_url(self) -> str:
        """Return target_url or fallback to url."""
        if self.target_url is not None:
            return str(self.target_url)
        if self.url is not None:
            return str(self.url)
        raise ValueError("Either target_url or url must be provided")

    class Config:
        from_attributes = True


class GenerateResponse(BaseModel):
    job_id: str
    session_id: str

    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # e.g., pending, processing, completed, failed
    progress: int  # percentage, 0-100
    step_statuses: list[str]  # list of statuses for each step
    result_url: str | None = None
    error: str | None = None

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    message: ChatMessage

    class Config:
        from_attributes = True


class ErrorResponseError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
    request_id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    error: ErrorResponseError

    class Config:
        from_attributes = True

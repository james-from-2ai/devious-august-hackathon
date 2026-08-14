"""Request and response schemas for the advisory service.

The judge validates against these exact shapes. A response that does not
parse scores 0 as SCHEMA_ERROR, so do not change field names or types.
You are free to change everything behind the schema.

Block 2 changes the questions in a way that is announced at 12:30. Requests
may carry extra fields then; pydantic ignores fields it does not know, so
this schema keeps working unmodified.
"""

from typing import Literal

from pydantic import BaseModel, Field


class AdviseRequest(BaseModel):
    question: str
    district: str
    language: Literal["en", "hi", "te"]


class AdviseResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    block: int
    team: str

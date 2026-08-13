"""Request and response schemas for the advisory service.

Block 1 is text in, text out. Block 2 adds audio via the V2 models at the
bottom of this file; the text answer stays mandatory in both.

The scorer validates against these exact shapes. A response that does not
parse scores 0 as SCHEMA_ERROR, so do not change field names or types.
You are free to change everything behind the schema.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AdviseRequest(BaseModel):
    question: str
    district: str
    language: Literal["en", "hi", "te"]


class AdviseResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str]


class AdviseRequestV2(BaseModel):
    """Block 2. Audio in, text out, audio out for bonus points."""

    question_audio: str                 # base64 ogg/opus
    question_transcript: str            # degraded ASR output, provided as-is
    district: str
    language: Literal["hi", "te"]


class AdviseResponseV2(BaseModel):
    answer: str                         # required, always scored
    answer_audio: Optional[str] = None  # base64 ogg/opus, optional bonus
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    block: int
    team: str

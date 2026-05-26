import re
from typing import Optional
from pydantic import BaseModel, field_validator


import datetime


class CastRequest(BaseModel):
    date: str  # "2026-05-26"
    time: str  # "21:30"
    yao_code: str  # "678976" (6 chars, each 6|7|8|9)
    question: str = ""

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            datetime.date.fromisoformat(v)
        except ValueError:
            raise ValueError("date must be YYYY-MM-DD format")
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        try:
            datetime.time.fromisoformat(v)
        except ValueError:
            raise ValueError("time must be HH:MM format")
        return v

    @field_validator("yao_code")
    @classmethod
    def validate_yao_code(cls, v: str) -> str:
        if len(v) != 6 or not re.fullmatch(r"[6789]{6}", v):
            raise ValueError("yao_code must be exactly 6 digits, each 6-9")
        return v


class CastResponse(BaseModel):
    cast_id: str
    date: str
    time: str
    yao_code: str
    question: str
    pan_result: str


class AISettings(BaseModel):
    base_url: str = ""
    model: str = "gpt-3.5-turbo"
    api_key: str = ""
    temperature: float = 0.7
    system_prompt: str = ""
    user_prompt_template: str = ""
    max_tokens: Optional[int] = None
    timeout: float = 60.0
    max_retries: int = 3


class InterpretRequest(BaseModel):
    question: str
    pan_result: str
    settings: AISettings


class InterpretResponse(BaseModel):
    content: str


class ValidateKeyRequest(BaseModel):
    base_url: str = ""
    api_key: str
    model: str = "gpt-3.5-turbo"


class ValidateKeyResponse(BaseModel):
    valid: bool
    message: str


class TextItem(BaseModel):
    name: str
    title: str


class TextsResponse(BaseModel):
    texts: list[TextItem]


class TextContentResponse(BaseModel):
    name: str
    title: str
    content: str

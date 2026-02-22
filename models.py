from pydantic import BaseModel, validator
from typing import List, Optional

class poll_details(BaseModel):
    poll_id: str = ""
    question: str
    options: List[str]
    response: List[int] = []
    expires_at: Optional[str] = ""

    @validator("question")
    def question_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Question must not be empty")
        return v.strip()

    @validator("options")
    def min_two_options(cls, v):
        cleaned = [o.strip() for o in v if o.strip()]
        if len(cleaned) < 2:
            raise ValueError("Poll must have at least 2 non-empty options")
        return cleaned

class update_poll_details(BaseModel):
    poll_id: str
    question: str = ""
    options: List[str] = []
    response: List[int] = []
    pollOption: int = 0
    expires_at: Optional[str] = ""

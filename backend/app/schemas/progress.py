from datetime import datetime
from pydantic import BaseModel


class ProgressOut(BaseModel):
    word_id: int
    english: str
    chinese: str
    status: str
    correct_count: int
    wrong_count: int
    next_review_at: datetime | None


class ProgressSummary(BaseModel):
    total_words: int
    new_count: int
    learning_count: int
    mastered_count: int


class ProgressUpdateRequest(BaseModel):
    knew_it: bool

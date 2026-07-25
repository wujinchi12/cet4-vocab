from pydantic import BaseModel, Field
from datetime import datetime


class FeedbackCreate(BaseModel):
    type: str = Field(..., pattern="^(suggestion|bug)$")
    content: str = Field(..., min_length=1, max_length=2000)
    contact: str | None = Field(None, max_length=200)


class FeedbackOut(BaseModel):
    id: int
    user_id: int | None
    type: str
    content: str
    contact: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

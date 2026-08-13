from pydantic import BaseModel


class WordOut(BaseModel):
    id: int
    english: str
    chinese: str
    part_of_speech: str | None
    difficulty_level: int
    level: str
    phonetic: str | None

    model_config = {"from_attributes": True}


class WordDetailOut(WordOut):
    user_status: str | None = None
    correct_count: int | None = None
    wrong_count: int | None = None


class WordListResponse(BaseModel):
    items: list[WordOut]
    total: int
    page: int
    size: int

from pydantic import BaseModel


class QuizGenerateRequest(BaseModel):
    quiz_type: str
    count: int = 10
    direction: str = "en_to_cn"


class QuizAnswer(BaseModel):
    word_id: int
    answer: str


class QuizSubmitRequest(BaseModel):
    quiz_type: str
    direction: str = "en_to_cn"
    answers: list[QuizAnswer]


class GradedResult(BaseModel):
    word_id: int
    user_answer: str
    correct_answer: str
    is_correct: bool
    english: str
    chinese: str


class QuizResultResponse(BaseModel):
    total_questions: int
    correct_count: int
    wrong_count: int
    score_percent: float
    results: list[GradedResult]

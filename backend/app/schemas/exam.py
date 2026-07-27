from pydantic import BaseModel
from typing import Optional


class ExamPaperOut(BaseModel):
    id: int
    title: str
    year: int
    description: Optional[str] = None
    time_limit: int
    question_count: int = 0


class ExamQuestionOut(BaseModel):
    id: int
    paper_id: int
    question_type: str
    passage: Optional[str] = None
    question_text: str
    options: Optional[list[str]] = None
    order_num: int


class ExamPaperDetail(BaseModel):
    id: int
    title: str
    year: int
    description: Optional[str] = None
    time_limit: int
    questions: list[ExamQuestionOut]


class ExamAnswer(BaseModel):
    question_id: int
    answer: str


class ExamSubmitRequest(BaseModel):
    paper_id: int
    answers: list[ExamAnswer]
    time_spent: Optional[int] = None


class ExamResultItem(BaseModel):
    question_id: int
    question_type: str
    question_text: str
    your_answer: str
    correct_answer: str
    is_correct: bool
    word_id: Optional[int] = None
    english: str = ""
    chinese: str = ""


class ExamResultResponse(BaseModel):
    total_questions: int
    correct_count: int
    wrong_count: int
    score_percent: float
    results: list[ExamResultItem]


class ExamHistoryOut(BaseModel):
    id: int
    paper_title: str
    paper_year: int
    score: float
    total_questions: int
    correct_count: int
    time_spent: Optional[int] = None
    completed_at: str

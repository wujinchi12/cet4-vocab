from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    total_quizzes: int
    average_score: float
    highest_score: float

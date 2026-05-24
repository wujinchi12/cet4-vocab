from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.quiz_history import QuizHistory
from app.schemas.leaderboard import LeaderboardEntry

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[LeaderboardEntry])
def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            User.username,
            func.count(QuizHistory.id).label("total_quizzes"),
            func.avg(QuizHistory.score_percent).label("average_score"),
            func.max(QuizHistory.score_percent).label("highest_score"),
        )
        .join(QuizHistory, User.id == QuizHistory.user_id)
        .group_by(User.id, User.username)
        .having(func.count(QuizHistory.id) > 0)
        .order_by(func.avg(QuizHistory.score_percent).desc())
        .limit(limit)
        .all()
    )

    return [
        LeaderboardEntry(
            rank=i + 1,
            username=row.username,
            total_quizzes=row.total_quizzes,
            average_score=round(row.average_score, 1),
            highest_score=round(row.highest_score, 1),
        )
        for i, row in enumerate(rows)
    ]

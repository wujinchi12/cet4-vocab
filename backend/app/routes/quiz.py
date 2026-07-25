from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.quiz_history import QuizHistory
from app.schemas.quiz import (
    QuizGenerateRequest, QuizSubmitRequest,
    QuizResultResponse, GradedResult,
)
from app.services.quiz_generator import generate_quiz_questions, grade_answers

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.post("/generate", response_model=list[dict])
def generate_quiz(
    body: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    questions = generate_quiz_questions(
        db, body.quiz_type, body.count, body.direction, current_user.id
    )
    result = []
    for q in questions:
        item = {k: v for k, v in q.items() if k != "correct_answer"}
        result.append(item)
    return result


@router.post("/submit", response_model=QuizResultResponse)
def submit_quiz(
    body: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answers_for_grading = []
    for ans in body.answers:
        answers_for_grading.append({
            "word_id": ans.word_id,
            "answer": ans.answer,
        })

    correct, wrong, results = grade_answers(db, body.quiz_type, body.direction, answers_for_grading)
    score = (correct / (correct + wrong) * 100) if (correct + wrong) > 0 else 0

    history = QuizHistory(
        user_id=current_user.id,
        quiz_type=body.quiz_type,
        total_questions=correct + wrong,
        correct_count=correct,
        wrong_count=wrong,
        score_percent=score,
    )
    db.add(history)
    db.commit()

    graded = [GradedResult(**r) for r in results]
    return QuizResultResponse(
        total_questions=correct + wrong,
        correct_count=correct,
        wrong_count=wrong,
        score_percent=score,
        results=graded,
    )


@router.get("/history", response_model=list[dict])
def quiz_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = (
        db.query(QuizHistory)
        .filter(QuizHistory.user_id == current_user.id)
        .order_by(QuizHistory.completed_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": e.id,
            "quiz_type": e.quiz_type,
            "total_questions": e.total_questions,
            "correct_count": e.correct_count,
            "wrong_count": e.wrong_count,
            "score_percent": e.score_percent,
            "completed_at": e.completed_at.isoformat(),
        }
        for e in entries
    ]

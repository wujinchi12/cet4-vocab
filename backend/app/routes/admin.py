import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.user_progress import UserProgress
from app.models.quiz_history import QuizHistory
from app.models.feedback import Feedback
from app.auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])

ADMIN_KEY = os.getenv("ADMIN_KEY", "admin-secret-change-me")


def require_admin(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing admin token")
    token = authorization.removeprefix("Bearer ")
    if token != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin token")
    return token


@router.get("/users")
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        learned = db.query(func.count(UserProgress.id)).filter(
            UserProgress.user_id == u.id,
            UserProgress.correct_count > 0,
        ).scalar() or 0
        quiz_count = db.query(func.count(QuizHistory.id)).filter(
            QuizHistory.user_id == u.id
        ).scalar() or 0
        avg_score = db.query(func.avg(QuizHistory.score_percent)).filter(
            QuizHistory.user_id == u.id
        ).scalar()
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "words_learned": learned,
            "quiz_count": quiz_count,
            "avg_score": round(avg_score, 1) if avg_score else None,
        })
    return {"users": result, "total": len(result)}


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    learned = db.query(func.count(UserProgress.id)).filter(
        UserProgress.user_id == u.id,
        UserProgress.correct_count > 0,
    ).scalar() or 0
    quiz_count = db.query(func.count(QuizHistory.id)).filter(
        QuizHistory.user_id == u.id
    ).scalar() or 0
    avg_score = db.query(func.avg(QuizHistory.score_percent)).filter(
        QuizHistory.user_id == u.id
    ).scalar()
    recent_quizzes = db.query(QuizHistory).filter(
        QuizHistory.user_id == u.id
    ).order_by(QuizHistory.completed_at.desc()).limit(10).all()
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "words_learned": learned,
        "quiz_count": quiz_count,
        "avg_score": round(avg_score, 1) if avg_score else None,
        "recent_quizzes": [
            {
                "id": q.id,
                "quiz_type": q.quiz_type,
                "total_questions": q.total_questions,
                "correct_count": q.correct_count,
                "score_percent": q.score_percent,
                "completed_at": q.completed_at.isoformat() if q.completed_at else None,
            }
            for q in recent_quizzes
        ],
    }


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    db.query(UserProgress).filter(UserProgress.user_id == user_id).delete()
    db.query(QuizHistory).filter(QuizHistory.user_id == user_id).delete()
    db.delete(u)
    db.commit()
    return {"detail": f"User '{u.username}' deleted"}


@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    new_password = secrets.token_urlsafe(10)
    u.password_hash = hash_password(new_password)
    db.commit()
    return {"detail": "Password reset", "username": u.username, "new_password": new_password}


@router.get("/feedback")
def list_feedback(db: Session = Depends(get_db), _=Depends(require_admin)):
    items = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    return {
        "feedback": [
            {
                "id": f.id,
                "user_id": f.user_id,
                "type": f.type,
                "content": f.content,
                "contact": f.contact,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in items
        ],
        "total": len(items),
    }

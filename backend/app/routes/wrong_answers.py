from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.word import Word
from app.models.wrong_answer_book import WrongAnswerBook

router = APIRouter(prefix="/api/wrong-answers", tags=["wrong_answers"])


@router.post("/add")
def add_wrong_answers(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add wrong answers from a quiz result. body: { words: [{word_id, user_answer, correct_answer, quiz_type}] }"""
    words = body.get("words", [])
    added = 0
    for w in words:
        existing = (
            db.query(WrongAnswerBook)
            .filter(
                WrongAnswerBook.user_id == current_user.id,
                WrongAnswerBook.word_id == w["word_id"],
            )
            .first()
        )
        if existing:
            continue
        entry = WrongAnswerBook(
            user_id=current_user.id,
            word_id=w["word_id"],
            user_answer=w.get("user_answer", ""),
            correct_answer=w.get("correct_answer", ""),
            quiz_type=w.get("quiz_type", ""),
        )
        db.add(entry)
        added += 1
    db.commit()
    return {"added": added}


@router.get("")
def list_wrong_answers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(WrongAnswerBook)
        .filter(WrongAnswerBook.user_id == current_user.id)
        .order_by(WrongAnswerBook.created_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    word_ids = [it.word_id for it in items]
    words_map = {w.id: w for w in db.query(Word).filter(Word.id.in_(word_ids)).all()} if word_ids else {}

    result = []
    for it in items:
        w = words_map.get(it.word_id)
        result.append({
            "id": it.id,
            "word_id": it.word_id,
            "english": w.english if w else "",
            "chinese": w.chinese if w else "",
            "user_answer": it.user_answer,
            "correct_answer": it.correct_answer,
            "quiz_type": it.quiz_type,
            "reviewed": it.reviewed,
            "created_at": it.created_at.isoformat(),
        })
    return {"items": result, "total": total, "page": page, "size": size}


@router.get("/count")
def wrong_answer_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = (
        db.query(WrongAnswerBook.word_id)
        .filter(WrongAnswerBook.user_id == current_user.id)
        .distinct()
        .count()
    )
    return {"count": count}


@router.delete("/{word_id}")
def remove_wrong_answer(
    word_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = (
        db.query(WrongAnswerBook)
        .filter(
            WrongAnswerBook.user_id == current_user.id,
            WrongAnswerBook.word_id == word_id,
        )
        .first()
    )
    if not entry:
        return {"detail": "Not found"}
    db.delete(entry)
    db.commit()
    return {"detail": "Removed"}


@router.post("/clear")
def clear_wrong_answers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(WrongAnswerBook).filter(
        WrongAnswerBook.user_id == current_user.id
    ).delete()
    db.commit()
    return {"detail": "All cleared"}

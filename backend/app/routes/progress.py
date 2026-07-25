from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.word import Word
from app.models.user_progress import UserProgress
from app.schemas.progress import ProgressOut, ProgressSummary, ProgressUpdateRequest
from app.services.spaced_repetition import calculate_next_review, handle_wrong_answer

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("", response_model=ProgressSummary)
def get_progress_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    progress_entries = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()
    new_count = sum(1 for p in progress_entries if p.status == "new")
    learning_count = sum(1 for p in progress_entries if p.status == "learning")
    mastered_count = sum(1 for p in progress_entries if p.status == "mastered")
    return ProgressSummary(
        total_words=len(progress_entries),
        new_count=new_count,
        learning_count=learning_count,
        mastered_count=mastered_count,
    )


@router.get("/due", response_model=list[ProgressOut])
def get_due_words(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime
    now = datetime.utcnow()

    entries = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == current_user.id,
            (UserProgress.next_review_at <= now) | (UserProgress.next_review_at.is_(None)),
        )
        .limit(limit)
        .all()
    )

    result = []
    for entry in entries:
        word = db.query(Word).filter(Word.id == entry.word_id).first()
        if word:
            result.append(ProgressOut(
                word_id=word.id,
                english=word.english,
                chinese=word.chinese,
                status=entry.status,
                correct_count=entry.correct_count,
                wrong_count=entry.wrong_count,
                next_review_at=entry.next_review_at,
            ))

    # Fallback: new user with no progress records — return random words
    if not result:
        import random
        all_words = db.query(Word).all()
        if all_words:
            picked = random.sample(all_words, min(limit, len(all_words)))
            for word in picked:
                result.append(ProgressOut(
                    word_id=word.id,
                    english=word.english,
                    chinese=word.chinese,
                    status="new",
                    correct_count=0,
                    wrong_count=0,
                    next_review_at=None,
                ))

    return result


@router.get("/weakest", response_model=list[ProgressOut])
def get_weakest_words(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id)
        .order_by(UserProgress.wrong_count.desc(), UserProgress.correct_count.asc())
        .limit(limit)
        .all()
    )
    result = []
    for entry in entries:
        word = db.query(Word).filter(Word.id == entry.word_id).first()
        if word:
            result.append(ProgressOut(
                word_id=word.id,
                english=word.english,
                chinese=word.chinese,
                status=entry.status,
                correct_count=entry.correct_count,
                wrong_count=entry.wrong_count,
                next_review_at=entry.next_review_at,
            ))
    return result


@router.put("/{word_id}", response_model=ProgressOut)
def update_progress(
    word_id: int,
    body: ProgressUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id, UserProgress.word_id == word_id)
        .first()
    )

    if not progress:
        progress = UserProgress(user_id=current_user.id, word_id=word_id)
        db.add(progress)
        db.flush()

    if body.knew_it:
        progress.correct_count += 1
        new_status, next_review = calculate_next_review(progress.status, progress.correct_count)
    else:
        progress.wrong_count += 1
        new_status, next_review = handle_wrong_answer(progress.status)

    progress.status = new_status
    progress.next_review_at = next_review

    from datetime import datetime
    progress.last_reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    return ProgressOut(
        word_id=word.id,
        english=word.english,
        chinese=word.chinese,
        status=progress.status,
        correct_count=progress.correct_count,
        wrong_count=progress.wrong_count,
        next_review_at=progress.next_review_at,
    )

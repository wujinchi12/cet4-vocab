from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.word import Word
from app.models.favorite_word import FavoriteWord

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.post("/toggle")
def toggle_favorite(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    word_id = body.get("word_id")
    existing = (
        db.query(FavoriteWord)
        .filter(
            FavoriteWord.user_id == current_user.id,
            FavoriteWord.word_id == word_id,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"favorited": False}
    db.add(FavoriteWord(user_id=current_user.id, word_id=word_id))
    db.commit()
    return {"favorited": True}


@router.get("")
def list_favorites(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(FavoriteWord)
        .filter(FavoriteWord.user_id == current_user.id)
        .order_by(FavoriteWord.created_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    word_ids = [it.word_id for it in items]
    words_map = {}
    if word_ids:
        words_map = {w.id: w for w in db.query(Word).filter(Word.id.in_(word_ids)).all()}

    result = []
    for it in items:
        w = words_map.get(it.word_id)
        result.append({
            "id": it.id,
            "word_id": it.word_id,
            "english": w.english if w else "",
            "chinese": w.chinese if w else "",
            "part_of_speech": w.part_of_speech if w else None,
            "created_at": it.created_at.isoformat(),
        })
    return {"items": result, "total": total, "page": page, "size": size}


@router.delete("/{word_id}")
def remove_favorite(
    word_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = (
        db.query(FavoriteWord)
        .filter(
            FavoriteWord.user_id == current_user.id,
            FavoriteWord.word_id == word_id,
        )
        .first()
    )
    if not entry:
        return {"detail": "Not found"}
    db.delete(entry)
    db.commit()
    return {"detail": "Removed"}


@router.post("/clear")
def clear_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(FavoriteWord).filter(
        FavoriteWord.user_id == current_user.id
    ).delete()
    db.commit()
    return {"detail": "All cleared"}

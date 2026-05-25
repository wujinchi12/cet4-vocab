from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.word import Word
from app.schemas.word import WordOut, WordDetailOut, WordListResponse

router = APIRouter(prefix="/api/words", tags=["words"])


@router.get("", response_model=WordListResponse)
def list_words(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str = Query("", max_length=100),
    db: Session = Depends(get_db),
):
    query = db.query(Word)
    if search:
        query = query.filter(
            Word.english.like(f"%{search}%") | Word.chinese.like(f"%{search}%")
        )
    total = query.count()
    items = query.order_by(Word.id).offset((page - 1) * size).limit(size).all()
    return WordListResponse(
        items=[WordOut.model_validate(w) for w in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{word_id}", response_model=WordDetailOut)
def get_word(word_id: int, db: Session = Depends(get_db)):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return WordDetailOut.model_validate(word)

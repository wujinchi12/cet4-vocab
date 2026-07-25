from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackOut, status_code=201)
def submit_feedback(body: FeedbackCreate, db: Session = Depends(get_db)):
    feedback = Feedback(
        type=body.type,
        content=body.content,
        contact=body.contact,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

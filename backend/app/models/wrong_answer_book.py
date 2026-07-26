from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.database import Base


class WrongAnswerBook(Base):
    __tablename__ = "wrong_answer_book"
    __table_args__ = (UniqueConstraint("user_id", "word_id"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    user_answer = Column(String, nullable=True)
    correct_answer = Column(String, nullable=False)
    quiz_type = Column(String(20), nullable=True)
    reviewed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

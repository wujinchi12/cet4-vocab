from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class ExamPaper(Base):
    __tablename__ = "exam_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    time_limit = Column(Integer, default=120)

    questions = relationship("ExamQuestion", order_by="ExamQuestion.order_num")


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("exam_papers.id"), nullable=False)
    question_type = Column(String(20), nullable=False)
    passage = Column(Text, nullable=True)
    question_text = Column(String, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String, nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=True)
    order_num = Column(Integer, nullable=False)

    paper = relationship("ExamPaper", back_populates="questions")


class ExamHistory(Base):
    __tablename__ = "exam_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("exam_papers.id"), nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    time_spent = Column(Integer, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

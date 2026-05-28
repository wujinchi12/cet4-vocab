from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    english = Column(String, nullable=False, unique=True, index=True)
    chinese = Column(String, nullable=False)
    part_of_speech = Column(String, nullable=True)
    difficulty_level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    contact = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

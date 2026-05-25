import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

# Auto-seed words on first launch
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
try:
    from scripts.seed_words import seed
    seed()
except Exception as e:
    logger.error(f"Seed failed: {e}")

app = FastAPI(title="CET-4 Vocabulary API")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes import auth, words, progress, quiz, leaderboard

app.include_router(auth.router)
app.include_router(words.router)
app.include_router(progress.router)
app.include_router(quiz.router)
app.include_router(leaderboard.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}

import traceback
@app.get("/api/debug")
def debug():
    from app.database import SessionLocal
    from app.models.word import Word
    try:
        db = SessionLocal()
        count = db.query(Word).count()
        db.close()
        return {"word_count": count}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

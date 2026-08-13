import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, ensure_schema

Base.metadata.create_all(bind=engine)
ensure_schema()

# Run data enrichment on startup (idempotent — only adds missing words / updates null POS)
try:
    from scripts.enrich_words import enrich
    enrich()
except Exception:
    pass

app = FastAPI(title="CET Vocabulary API")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    import traceback
    logging.getLogger(__name__).error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc(),
        },
    )

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes import auth, words, progress, quiz, leaderboard, admin, feedback, wrong_answers, favorites, exam

app.include_router(auth.router)
app.include_router(words.router)
app.include_router(progress.router)
app.include_router(quiz.router)
app.include_router(leaderboard.router)
app.include_router(admin.router)
app.include_router(feedback.router)
app.include_router(wrong_answers.router)
app.include_router(favorites.router)
app.include_router(exam.router)

# Seed exam data on startup (idempotent)
try:
    from scripts.seed_exams import seed
    seed()
except Exception:
    pass

# Seed CET-6 words on startup (idempotent)
try:
    from scripts.seed_cet6 import seed as seed_cet6
    seed_cet6()
except Exception:
    pass

# Correct malformed CET-4 words on startup (idempotent)
try:
    from scripts.seed_fix_words import seed as seed_fix_words
    seed_fix_words()
except Exception:
    pass

# Backfill CET-4 phonetics on startup (idempotent)
try:
    from scripts.seed_cet4_phonetics import seed as seed_cet4_phonetics
    seed_cet4_phonetics()
except Exception:
    pass


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Serve frontend static files — must be after API routes
# Nixpacks build copies output to backend/static/; local dev uses pre-built files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.isdir(static_dir):
    static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(static_dir):

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API 404s should not be caught here
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        # If the path matches a real file, serve it
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Index directory requests (e.g. /admin/ -> /admin/index.html)
        if os.path.isdir(file_path) and os.path.isfile(os.path.join(file_path, "index.html")):
            return FileResponse(os.path.join(file_path, "index.html"))
        # SPA fallback: all unmatched paths serve index.html
        index = os.path.join(static_dir, "index.html")
        if os.path.isfile(index):
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="Not Found")

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CET-4 Vocabulary API")


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

from app.routes import auth, words, progress, quiz, leaderboard, admin

app.include_router(auth.router)
app.include_router(words.router)
app.include_router(progress.router)
app.include_router(quiz.router)
app.include_router(leaderboard.router)
app.include_router(admin.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Serve frontend static files — must be after API routes
# Prefer Nixpacks/Railway build output (frontend/dist), fall back to pre-built (static/)
_base = os.path.dirname(__file__)
nixpacks_dir = os.path.join(_base, "..", "..", "frontend", "dist")
prebuilt_dir = os.path.join(_base, "..", "static")
static_dir = nixpacks_dir if os.path.isdir(nixpacks_dir) else prebuilt_dir
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

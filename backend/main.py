import logging
from fastapi import FastAPI
from backend.api.routes import router
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI SOW Proposal Generator",
    description="Agent-based system for generating SOW proposals",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
def root():
    return {"message": "SOW Proposal Generator API"}


logger.info("FastAPI app ready -- routes mounted, CORS origins=%s", settings.CORS_ALLOW_ORIGINS)
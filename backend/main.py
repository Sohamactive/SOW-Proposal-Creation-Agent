from fastapi import FastAPI
from backend.api.routes import router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="AI SOW Proposal Generator",
    description="Agent-based system for generating SOW proposals",
    version="1.0"
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def root():
    return {"message": "SOW Proposal Generator API"}
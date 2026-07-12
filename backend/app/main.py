from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import engine, Base
from app.models import User, Resume, JobDescription, AnalysisResult
from app.routes.auth import router as auth_router
from app.routes.hr import router as hr_router
from app.routes.student import router as student_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="AI-powered resume analysis platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.upload_dir, exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory=settings.upload_dir),
    name="uploads"
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(hr_router, prefix="/api/hr", tags=["HR"])
app.include_router(student_router, prefix="/api/student", tags=["Student"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "running",
        "app": settings.app_name,
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to NextGen Resume Intelligence API",
        "docs": "/api/docs"
    }
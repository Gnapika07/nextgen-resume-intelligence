from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class JobDescriptionCreate(BaseModel):
    title: str
    company: Optional[str] = None
    description_text: str
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    required_experience: Optional[str] = None
    education_required: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Python Developer",
                "company": "TechCorp",
                "description_text": "We need a Python developer with FastAPI and SQL experience...",
                "required_skills": ["Python", "FastAPI", "SQL"],
                "required_experience": "2-4 years"
            }
        }


class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    description_text: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    required_experience: Optional[str] = None
    keywords: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisResultResponse(BaseModel):
    id: int
    resume_id: int
    jd_id: int
    overall_score: float
    skills_score: float
    experience_score: float
    keyword_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    extra_skills: List[str] = []
    rank: Optional[int] = None
    ai_summary: Optional[str] = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []
    score_breakdown: Dict = {}
    analyzed_at: datetime

    class Config:
        from_attributes = True


class CandidateRankingResponse(BaseModel):
    rank: int
    resume_id: int
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    overall_score: float
    skills_score: float
    experience_score: float
    keyword_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    experience_years: float = 0.0


class AnalyzeRequest(BaseModel):
    jd_id: int
    resume_ids: Optional[List[int]] = None
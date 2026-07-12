from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ResumeResponse(BaseModel):
    id: int
    filename: str
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_phone: Optional[str] = None
    skills: List[str] = []
    experience_years: float = 0.0
    education: List[dict] = []
    is_duplicate: str = "no"
    uploaded_at: datetime

    class Config:
        from_attributes = True


class BulkUploadResponse(BaseModel):
    total_uploaded: int
    successful: int
    duplicates: int
    failed: int
    resumes: List[ResumeResponse]
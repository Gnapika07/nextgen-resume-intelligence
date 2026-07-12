from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import UserRole
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.analysis_result import AnalysisResult
from app.schemas.resume import ResumeResponse
from app.schemas.analysis import JobDescriptionCreate, AnalysisResultResponse
from app.services.auth_service import get_current_user
from app.services.resume_parser import parse_resume
from app.services.nlp_engine import (
    analyze_resume_against_jd,
    extract_keywords_from_jd
)
from app.utils.file_handler import save_upload_file, compute_file_hash

router = APIRouter()
security = HTTPBearer()


def get_student_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Only student users can access these routes"""
    user = get_current_user(credentials.credentials, db)
    if user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Student access required"
        )
    return user


# ── RESUME UPLOAD ──

@router.post("/upload-resume", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user=Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """Student uploads their single resume"""

    file_path, ext, content = await save_upload_file(
        file, subfolder=f"student_{current_user.id}"
    )

    # Check for duplicate
    file_hash = compute_file_hash(content)
    existing = db.query(Resume).filter(
        Resume.file_hash == file_hash,
        Resume.user_id == current_user.id
    ).first()

    if existing:
        return existing

    # Parse the resume
    parsed = parse_resume(content, ext)

    # Delete old resume if student uploads a new one
    old_resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).first()

    if old_resume:
        db.delete(old_resume)
        db.commit()

    # Save new resume
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_type=ext.replace(".", ""),
        file_hash=file_hash,
        raw_text=parsed["raw_text"],
        candidate_name=parsed["candidate_name"],
        candidate_email=parsed["candidate_email"],
        candidate_phone=parsed["candidate_phone"],
        skills=parsed["skills"],
        experience_years=parsed["experience_years"],
        education=parsed["education"],
        work_experience=parsed["work_experience"],
        certifications=parsed["certifications"],
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


@router.get("/my-resume", response_model=ResumeResponse)
async def get_my_resume(
    current_user=Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """Get student's current resume"""
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="No resume found. Please upload your resume first."
        )

    return resume


# ── ANALYSIS ──

@router.post("/analyze")
async def analyze_my_resume(
    jd_data: JobDescriptionCreate,
    current_user=Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """
    Student analyzes their resume against a job description.
    They paste the JD text and get instant ATS-like scoring.
    """

    # Get student's resume
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Please upload your resume first"
        )

    # Auto-extract keywords from JD
    keywords = extract_keywords_from_jd(jd_data.description_text)

    # Build JD dict for NLP engine
    jd_dict = {
        "title": jd_data.title,
        "description_text": jd_data.description_text,
        "required_skills": jd_data.required_skills or [],
        "required_experience": jd_data.required_experience or "",
        "keywords": keywords
    }

    # Build resume dict
    resume_dict = {
        "candidate_name": resume.candidate_name,
        "raw_text": resume.raw_text or "",
        "skills": resume.skills or [],
        "experience_years": resume.experience_years or 0.0
    }

    # Run NLP analysis
    analysis = analyze_resume_against_jd(resume_dict, jd_dict)

    # Generate role recommendations based on skills
    recommended_roles = recommend_roles(resume.skills or [])

    # Save result to database
    existing = db.query(AnalysisResult).filter(
        AnalysisResult.resume_id == resume.id,
        AnalysisResult.jd_id == 0
    ).first()

    # Create a temporary JD record for student analysis
    temp_jd = JobDescription(
        hr_user_id=current_user.id,
        title=jd_data.title,
        company=jd_data.company or "Target Company",
        description_text=jd_data.description_text,
        required_skills=jd_data.required_skills or [],
        keywords=keywords
    )
    db.add(temp_jd)
    db.commit()
    db.refresh(temp_jd)

    result = AnalysisResult(
        resume_id=resume.id,
        jd_id=temp_jd.id,
        overall_score=analysis["overall_score"],
        skills_score=analysis["skills_score"],
        experience_score=analysis["experience_score"],
        keyword_score=analysis["keyword_score"],
        matched_skills=analysis["matched_skills"],
        missing_skills=analysis["missing_skills"],
        extra_skills=analysis["extra_skills"],
        strengths=analysis["strengths"],
        weaknesses=analysis["weaknesses"],
        suggestions=analysis["suggestions"],
        score_breakdown=analysis["score_breakdown"],
        recommended_roles=recommended_roles,
        rank=1
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    # Return comprehensive student-friendly response
    return {
        "candidate_name": resume.candidate_name,
        "job_title": jd_data.title,
        "overall_score": analysis["overall_score"],
        "score_label": get_score_label(analysis["overall_score"]),
        "skills_score": analysis["skills_score"],
        "experience_score": analysis["experience_score"],
        "keyword_score": analysis["keyword_score"],
        "matched_skills": analysis["matched_skills"],
        "missing_skills": analysis["missing_skills"],
        "your_skills": resume.skills or [],
        "strengths": analysis["strengths"],
        "weaknesses": analysis["weaknesses"],
        "suggestions": analysis["suggestions"],
        "score_breakdown": analysis["score_breakdown"],
        "recommended_roles": recommended_roles,
        "ats_tip": get_ats_tip(analysis["overall_score"])
    }


@router.get("/my-results")
async def get_my_results(
    current_user=Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """Get all analysis results for the student"""
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="No resume found"
        )

    results = db.query(AnalysisResult).filter(
        AnalysisResult.resume_id == resume.id
    ).order_by(AnalysisResult.analyzed_at.desc()).all()

    response = []
    for result in results:
        jd = db.query(JobDescription).filter(
            JobDescription.id == result.jd_id
        ).first()

        response.append({
            "analysis_id": result.id,
            "job_title": jd.title if jd else "Unknown",
            "overall_score": result.overall_score,
            "score_label": get_score_label(result.overall_score),
            "matched_skills": result.matched_skills or [],
            "missing_skills": result.missing_skills or [],
            "suggestions": result.suggestions or [],
            "analyzed_at": result.analyzed_at.isoformat()
        })

    return response


@router.get("/job-roles")
async def get_recommended_roles(
    current_user=Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """Get job role recommendations based on student's skills"""
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Please upload your resume first"
        )

    roles = recommend_roles(resume.skills or [])

    return {
        "candidate_name": resume.candidate_name,
        "your_skills": resume.skills or [],
        "recommended_roles": roles
    }


# ── HELPER FUNCTIONS ──

def get_score_label(score: float) -> str:
    """Convert numeric score to human-readable label"""
    if score >= 85:
        return "Excellent Match"
    elif score >= 70:
        return "Strong Match"
    elif score >= 55:
        return "Good Match"
    elif score >= 40:
        return "Partial Match"
    else:
        return "Low Match — Needs Improvement"


def get_ats_tip(score: float) -> str:
    """Give ATS-specific advice based on score"""
    if score >= 85:
        return "Your resume is highly optimized for ATS systems. Great job!"
    elif score >= 70:
        return "Your resume passes most ATS filters. Minor improvements can boost your score."
    elif score >= 55:
        return "Your resume may get filtered by strict ATS systems. Add more relevant keywords."
    else:
        return "Your resume needs significant optimization to pass ATS filters. Focus on adding missing skills and keywords."


def recommend_roles(skills: List[str]) -> List[str]:
    """
    Recommend job roles based on candidate's skills.
    Simple rule-based recommendation system.
    """
    skills_lower = [s.lower() for s in skills]
    roles = []

    # Data Science / ML
    ml_skills = {"python", "machine learning", "tensorflow", "pytorch",
                 "scikit-learn", "pandas", "numpy", "data analysis"}
    if len(ml_skills.intersection(skills_lower)) >= 3:
        roles.append("Machine Learning Engineer")
        roles.append("Data Scientist")
        roles.append("AI Research Engineer")

    # Web Development
    web_skills = {"react", "html", "css", "javascript", "nodejs",
                  "typescript", "vue", "angular"}
    if len(web_skills.intersection(skills_lower)) >= 3:
        roles.append("Frontend Developer")
        roles.append("Full Stack Developer")
        roles.append("UI/UX Developer")

    # Backend Development
    backend_skills = {"python", "fastapi", "django", "flask",
                      "sql", "postgresql", "rest api"}
    if len(backend_skills.intersection(skills_lower)) >= 3:
        roles.append("Backend Developer")
        roles.append("API Developer")
        roles.append("Python Developer")

    # Data Engineering
    data_skills = {"sql", "pandas", "power bi", "tableau",
                   "data visualization", "spark", "hadoop"}
    if len(data_skills.intersection(skills_lower)) >= 3:
        roles.append("Data Analyst")
        roles.append("Business Intelligence Developer")
        roles.append("Data Engineer")

    # Cloud / DevOps
    cloud_skills = {"aws", "azure", "docker", "kubernetes",
                    "git", "ci/cd", "linux"}
    if len(cloud_skills.intersection(skills_lower)) >= 3:
        roles.append("DevOps Engineer")
        roles.append("Cloud Engineer")
        roles.append("Site Reliability Engineer")

    # Remove duplicates
    seen = set()
    unique_roles = []
    for role in roles:
        if role not in seen:
            seen.add(role)
            unique_roles.append(role)

    return unique_roles if unique_roles else [
        "Software Developer",
        "Junior Developer",
        "Technical Analyst"
    ]
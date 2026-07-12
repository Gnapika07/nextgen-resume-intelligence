from app.services.ai_summarizer import generate_ai_summary
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import csv

from app.database import get_db
from app.models.user import UserRole
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.analysis_result import AnalysisResult
from app.schemas.resume import ResumeResponse, BulkUploadResponse
from app.schemas.analysis import (
    JobDescriptionCreate, JobDescriptionResponse,
    AnalyzeRequest, CandidateRankingResponse
)
from app.services.auth_service import get_current_user
from app.services.resume_parser import parse_resume
from app.services.nlp_engine import (
    analyze_resume_against_jd,
    rank_candidates,
    extract_keywords_from_jd
)
from app.utils.file_handler import save_upload_file, compute_file_hash
from app.config import settings

router = APIRouter()
security = HTTPBearer()


def get_hr_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Only HR users can access these routes"""
    user = get_current_user(credentials.credentials, db)
    if user.role != UserRole.HR:
        raise HTTPException(
            status_code=403,
            detail="HR access required"
        )
    return user


# ── RESUME UPLOAD ──

@router.post("/upload-resumes", response_model=BulkUploadResponse)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    current_user=Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Upload 1-100 resumes at once"""
    if len(files) > settings.max_resumes_per_batch:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.max_resumes_per_batch} resumes per upload"
        )

    results = []
    duplicates = 0
    failed = 0

    for file in files:
        try:
            file_path, ext, content = await save_upload_file(
                file, subfolder=f"hr_{current_user.id}"
            )

            file_hash = compute_file_hash(content)
            existing = db.query(Resume).filter(
                Resume.file_hash == file_hash
            ).first()

            if existing:
                duplicates += 1
                existing.is_duplicate = "yes"
                results.append(existing)
                continue

            parsed = parse_resume(content, ext)

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
            results.append(resume)

        except Exception as e:
            print(f"Failed to process {file.filename}: {e}")
            failed += 1

    return {
        "total_uploaded": len(files),
        "successful": len(results) - duplicates,
        "duplicates": duplicates,
        "failed": failed,
        "resumes": results
    }


@router.get("/resumes", response_model=List[ResumeResponse])
async def get_resumes(
    current_user=Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Get all resumes uploaded by this HR user"""
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).all()
    return resumes


@router.get("/duplicates", response_model=List[ResumeResponse])
async def get_duplicates(
    current_user=Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Get all duplicate resumes"""
    duplicates = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_duplicate == "yes"
    ).all()
    return duplicates


# ── JOB DESCRIPTION ──

@router.post("/upload-jd", response_model=JobDescriptionResponse)
async def upload_job_description(
    jd_data: JobDescriptionCreate,
    current_user=Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Create a new Job Description"""

    # Auto-extract keywords from JD text
    keywords = extract_keywords_from_jd(jd_data.description_text)

    jd = JobDescription(
        hr_user_id=current_user.id,
        title=jd_data.title,
        company=jd_data.company,
        description_text=jd_data.description_text,
        required_skills=jd_data.required_skills,
        preferred_skills=jd_data.preferred_skills,
        required_experience=jd_data.required_experience,
        education_required=jd_data.education_required,
        keywords=keywords
    )

    db.add(jd)
    db.commit()
    db.refresh(jd)

    return jd


@router.get("/job-descriptions", response_model=List[JobDescriptionResponse])
async def get_job_descriptions(
    current_user=Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Get all JDs created by this HR user"""
    jds = db.query(JobDescription).filter(
        JobDescription.hr_user_id == current_user.id
    ).all()
    return jds


# ── ANALYSIS ──

@router.post("/analyze")
async def analyze_resumes(
    request: AnalyzeRequest,
    current_user=Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """
    Run NLP analysis — compare resumes against a Job Description.
    This is the core AI feature of the HR dashboard.
    """

    # Get the job description
    jd = db.query(JobDescription).filter(
        JobDescription.id == request.jd_id,
        JobDescription.hr_user_id == current_user.id
    ).first()

    if not jd:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    # Get resumes to analyze
    if request.resume_ids:
        resumes = db.query(Resume).filter(
            Resume.id.in_(request.resume_ids),
            Resume.user_id == current_user.id
        ).all()
    else:
        # Analyze ALL resumes if no specific IDs given
        resumes = db.query(Resume).filter(
            Resume.user_id == current_user.id,
            Resume.is_duplicate != "yes"
        ).all()

    if not resumes:
        raise HTTPException(
            status_code=404,
            detail="No resumes found to analyze"
        )

    # Convert JD to dict for NLP engine
    jd_dict = {
        "title": jd.title,
        "description_text": jd.description_text,
        "required_skills": jd.required_skills or [],
        "preferred_skills": jd.preferred_skills or [],
        "required_experience": jd.required_experience or "",
        "keywords": jd.keywords or []
    }

    # Run analysis on each resume
    all_analyses = []
    for resume in resumes:
        resume_dict = {
            "candidate_name": resume.candidate_name,
            "raw_text": resume.raw_text or "",
            "skills": resume.skills or [],
            "experience_years": resume.experience_years or 0.0
        }

        analysis = analyze_resume_against_jd(resume_dict, jd_dict)
        # Generate AI summary
        ai_summary = generate_ai_summary(
            candidate_name=resume.candidate_name or "Candidate",
            skills=resume.skills or [],
            experience_years=resume.experience_years or 0,
            overall_score=analysis["overall_score"],
            matched_skills=analysis["matched_skills"],
            missing_skills=analysis["missing_skills"],
            job_title=jd.title
        )
        analysis["ai_summary"] = ai_summary
        analysis["resume_id"] = resume.id
        analysis["resume"] = resume
        all_analyses.append(analysis)

    # Rank all candidates
    ranked = rank_candidates(all_analyses)

    # Save results to database
    saved_results = []
    for analysis in ranked:
        # Check if result already exists — update it
        existing = db.query(AnalysisResult).filter(
            AnalysisResult.resume_id == analysis["resume_id"],
            AnalysisResult.jd_id == jd.id
        ).first()

        if existing:
            existing.overall_score = analysis["overall_score"]
            existing.skills_score = analysis["skills_score"]
            existing.experience_score = analysis["experience_score"]
            existing.keyword_score = analysis["keyword_score"]
            existing.ai_summary = analysis.get("ai_summary", "")
            existing.matched_skills = analysis["matched_skills"]
            existing.missing_skills = analysis["missing_skills"]
            existing.extra_skills = analysis["extra_skills"]
            existing.rank = analysis["rank"]
            existing.strengths = analysis["strengths"]
            existing.weaknesses = analysis["weaknesses"]
            existing.suggestions = analysis["suggestions"]
            existing.score_breakdown = analysis["score_breakdown"]
            db.commit()
            saved_results.append(existing)
        else:
            result = AnalysisResult(
                resume_id=analysis["resume_id"],
                jd_id=jd.id,
                overall_score=analysis["overall_score"],
                skills_score=analysis["skills_score"],
                experience_score=analysis["experience_score"],
                keyword_score=analysis["keyword_score"],
                matched_skills=analysis["matched_skills"],
                missing_skills=analysis["missing_skills"],
                extra_skills=analysis["extra_skills"],
                rank=analysis["rank"],
                strengths=analysis["strengths"],
                weaknesses=analysis["weaknesses"],
                suggestions=analysis["suggestions"],
                score_breakdown=analysis["score_breakdown"],
                ai_summary=analysis.get("ai_summary", ""),
            )
            db.add(result)
            db.commit()
            db.refresh(result)
            saved_results.append(result)

    return {
        "message": f"Analysis complete for {len(resumes)} resumes",
        "jd_title": jd.title,
        "total_analyzed": len(resumes),
        "results_saved": len(saved_results)
    }


# ── RESULTS ──

@router.get("/results/{jd_id}", response_model=List[CandidateRankingResponse])
async def get_results(
    jd_id: int,
    current_user=Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Get ranked candidates for a specific Job Description"""

    # Verify JD belongs to this HR user
    jd = db.query(JobDescription).filter(
        JobDescription.id == jd_id,
        JobDescription.hr_user_id == current_user.id
    ).first()

    if not jd:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    # Get all results for this JD ordered by rank
    results = db.query(AnalysisResult).filter(
        AnalysisResult.jd_id == jd_id
    ).order_by(AnalysisResult.rank).all()

    # Build response with candidate details
    response = []
    for result in results:
        resume = db.query(Resume).filter(
            Resume.id == result.resume_id
        ).first()

        response.append({
            "rank": result.rank or 0,
            "resume_id": result.resume_id,
            "candidate_name": resume.candidate_name if resume else "Unknown",
            "candidate_email": resume.candidate_email if resume else None,
            "overall_score": result.overall_score,
            "skills_score": result.skills_score,
            "experience_score": result.experience_score,
            "keyword_score": result.keyword_score,
            "matched_skills": result.matched_skills or [],
            "missing_skills": result.missing_skills or [],
            "strengths": result.strengths or [],
            "weaknesses": result.weaknesses or [],
            "experience_years": resume.experience_years if resume else 0.0
        })

    return response


# ── EXPORT FOR POWER BI ──

@router.get("/export/{jd_id}")
async def export_results_csv(
    jd_id: int,
    current_user=Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """
    Export analysis results as CSV for Power BI.
    Power BI can directly import this CSV file.
    """
    jd = db.query(JobDescription).filter(
        JobDescription.id == jd_id,
        JobDescription.hr_user_id == current_user.id
    ).first()

    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    results = db.query(AnalysisResult).filter(
        AnalysisResult.jd_id == jd_id
    ).order_by(AnalysisResult.rank).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Headers
    writer.writerow([
        "Rank", "Candidate Name", "Email",
        "Overall Score", "Skills Score",
        "Experience Score", "Keyword Score",
        "Experience Years", "Matched Skills",
        "Missing Skills", "JD Title"
    ])

    # CSV Rows
    for result in results:
        resume = db.query(Resume).filter(
            Resume.id == result.resume_id
        ).first()

        writer.writerow([
            result.rank,
            resume.candidate_name if resume else "Unknown",
            resume.candidate_email if resume else "",
            result.overall_score,
            result.skills_score,
            result.experience_score,
            result.keyword_score,
            resume.experience_years if resume else 0,
            ", ".join(result.matched_skills or []),
            ", ".join(result.missing_skills or []),
            jd.title
        ])

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=results_jd_{jd_id}.csv"
        }
    )
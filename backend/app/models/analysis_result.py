from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    overall_score = Column(Float, default=0.0)
    skills_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    keyword_score = Column(Float, default=0.0)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    extra_skills = Column(JSON, default=list)
    rank = Column(Integer, nullable=True)
    ai_summary = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    recommended_roles = Column(JSON, default=list)
    score_breakdown = Column(JSON, default=dict)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="analysis_results")
    job_description = relationship("JobDescription", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult score={self.overall_score}>"
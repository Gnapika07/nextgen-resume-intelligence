from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_hash = Column(String(64), nullable=True)
    raw_text = Column(Text, nullable=True)
    candidate_name = Column(String(255), nullable=True)
    candidate_email = Column(String(255), nullable=True)
    candidate_phone = Column(String(50), nullable=True)
    skills = Column(JSON, default=list)
    experience_years = Column(Float, default=0.0)
    education = Column(JSON, default=list)
    work_experience = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_duplicate = Column(String(10), default="no")

    owner = relationship("User", back_populates="resumes")
    analysis_results = relationship("AnalysisResult", back_populates="resume")

    def __repr__(self):
        return f"<Resume {self.filename}>"
import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.resume import Resume


def compute_sha256(content: bytes) -> str:
    """Generate SHA-256 hash of file content"""
    return hashlib.sha256(content).hexdigest()


def find_duplicate(
    db: Session,
    file_hash: str,
    user_id: int
) -> Optional[Resume]:
    """
    Check if a resume with the same hash already exists.
    Same hash = identical file = duplicate.
    """
    return db.query(Resume).filter(
        Resume.file_hash == file_hash,
        Resume.user_id == user_id
    ).first()


def get_all_duplicates(
    db: Session,
    user_id: int
) -> List[Resume]:
    """Get all duplicate resumes for an HR user"""
    return db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.is_duplicate == "yes"
    ).all()


def mark_as_duplicate(
    db: Session,
    resume_id: int
) -> None:
    """Mark a resume as duplicate"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if resume:
        resume.is_duplicate = "yes"
        db.commit()
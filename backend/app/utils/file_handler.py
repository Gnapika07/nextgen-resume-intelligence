import os
import hashlib
import aiofiles
from fastapi import UploadFile, HTTPException
from app.config import settings


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def validate_file(file: UploadFile) -> None:
    """Check file type and size are acceptable"""
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Only PDF and DOCX accepted."
        )


def compute_file_hash(file_content: bytes) -> str:
    """
    Generate a unique fingerprint for a file.
    Used for duplicate detection — if two files have the same hash,
    they are identical files.
    """
    return hashlib.sha256(file_content).hexdigest()


async def save_upload_file(file: UploadFile, subfolder: str = "") -> tuple[str, str, bytes]:
    """
    Save an uploaded file to disk.
    Returns: (file_path, file_extension, file_content)
    """
    validate_file(file)

    # Read file content
    content = await file.read()

    # Check file size
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {settings.max_file_size_mb}MB"
        )

    # Create subfolder if needed
    save_dir = os.path.join(settings.upload_dir, subfolder)
    os.makedirs(save_dir, exist_ok=True)

    # Create unique filename to avoid overwrites
    file_hash = compute_file_hash(content)
    ext = get_file_extension(file.filename)
    unique_filename = f"{file_hash[:16]}_{file.filename}"
    file_path = os.path.join(save_dir, unique_filename)

    # Save to disk
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return file_path, ext, content
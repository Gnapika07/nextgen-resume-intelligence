from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    HR = "hr"
    STUDENT = "student"


# ── REQUEST SCHEMAS (data coming IN) ──

class UserRegister(BaseModel):
    """Data needed to register a new user"""
    email: EmailStr          # validates it's a real email format
    full_name: str
    password: str
    role: UserRole           # must be "hr" or "student"

    class Config:
        # Example shown in API docs
        json_schema_extra = {
            "example": {
                "email": "hr@company.com",
                "full_name": "John Smith",
                "password": "strongpassword123",
                "role": "hr"
            }
        }


class UserLogin(BaseModel):
    """Data needed to login"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "hr@company.com",
                "password": "strongpassword123"
            }
        }


# ── RESPONSE SCHEMAS (data going OUT) ──

class UserResponse(BaseModel):
    """What we send back about a user — NEVER include password!"""
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy models


class TokenResponse(BaseModel):
    """Returned after successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, MessageResponse
from app.services.auth_service import register_user, login_user, get_current_user

# APIRouter groups related endpoints together
router = APIRouter()

# HTTPBearer extracts the token from Authorization header
security = HTTPBearer()


def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> object:
    """
    FastAPI dependency — extracts and validates JWT token.
    Add this to any route that needs authentication.
    """
    return get_current_user(credentials.credentials, db)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new HR or Student account.
    """
    user = register_user(db, user_data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login and receive a JWT access token.
    Use this token in the Authorization header for protected routes.
    """
    result = login_user(db, login_data)
    return result


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user_dependency)):
    """
    Get the currently logged-in user's profile.
    Requires Authorization: Bearer <token>
    """
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user=Depends(get_current_user_dependency)):
    """
    Logout — on the frontend, just delete the token from localStorage.
    JWT tokens are stateless so server-side logout just confirms the action.
    """
    return {
        "message": f"Successfully logged out. Goodbye {current_user.full_name}!",
        "success": True
    }
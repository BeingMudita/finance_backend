from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT token",
)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email + password.
    Returns a Bearer JWT token valid for the configured expiry window.
    """
    return AuthService(db).login(credentials)
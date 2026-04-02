from sqlalchemy.orm import Session

from app.core.exceptions import AuthError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, credentials: LoginRequest) -> TokenResponse:
        user = (
            self.db.query(User)
            .filter(User.email == credentials.email, User.is_deleted == False)  # noqa: E712
            .first()
        )

        if user is None or not verify_password(credentials.password, user.hashed_password):
            raise AuthError("Invalid email or password")

        if not user.is_active:
            raise AuthError("Account is deactivated. Please contact an administrator.")

        token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        return TokenResponse(access_token=token)
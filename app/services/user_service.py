from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_404(self, user_id: int) -> User:
        user = self.db.query(User).filter(
            User.id == user_id, User.is_deleted == False  # noqa: E712
        ).first()
        if not user:
            raise NotFoundError("User", user_id)
        return user

    def create_user(self, payload: UserCreate) -> UserResponse:
        existing = self.db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise ConflictError(f"Email '{payload.email}' is already registered")

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.model_validate(user)

    def get_user(self, user_id: int) -> UserResponse:
        return UserResponse.model_validate(self._get_or_404(user_id))

    def list_users(self, page: int = 1, page_size: int = 20) -> UserListResponse:
        query = self.db.query(User).filter(User.is_deleted == False)  # noqa: E712
        total = query.count()
        users = query.offset((page - 1) * page_size).limit(page_size).all()
        return UserListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[UserResponse.model_validate(u) for u in users],
        )

    def update_user(self, user_id: int, payload: UserUpdate) -> UserResponse:
        user = self._get_or_404(user_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.model_validate(user)

    def soft_delete_user(self, user_id: int, requesting_user_id: int) -> None:
        if user_id == requesting_user_id:
            from app.core.exceptions import AppError
            from fastapi import status
            raise AppError("You cannot delete your own account", status.HTTP_400_BAD_REQUEST)
        user = self._get_or_404(user_id)
        user.is_deleted = True
        user.is_active = False
        self.db.commit()

    def ensure_admin_exists(self, email: str, password: str) -> None:
        """Called at startup to seed the first admin if none exists."""
        admin_exists = self.db.query(User).filter(User.role == UserRole.admin).first()
        if not admin_exists:
            user = User(
                email=email,
                full_name="System Admin",
                hashed_password=hash_password(password),
                role=UserRole.admin,
            )
            self.db.add(user)
            self.db.commit()
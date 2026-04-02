from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.rbac import require_admin
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user [Admin only]",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return UserService(db).create_user(payload)


@router.get(
    "",
    response_model=UserListResponse,
    summary="List all users with pagination [Admin only]",
)
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return UserService(db).list_users(page, page_size)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a specific user by ID [Admin only]",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return UserService(db).get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user role or status [Admin only]",
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return UserService(db).update_user(user_id, payload)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Soft-delete a user [Admin only]",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    UserService(db).soft_delete_user(user_id, current_user.id)
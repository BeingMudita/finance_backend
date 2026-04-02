from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_active_user
from app.models.user import User, UserRole


def require_roles(*allowed_roles: UserRole):
    """
    Factory that returns a FastAPI dependency enforcing role-based access.

    Usage:
        @router.get("/admin-only")
        def admin_view(user: User = Depends(require_roles(UserRole.admin))):
            ...
    """

    def _checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return _checker


# Pre-built convenience guards
require_admin = require_roles(UserRole.admin)
require_analyst_or_above = require_roles(UserRole.analyst, UserRole.admin)
require_any_role = require_roles(UserRole.viewer, UserRole.analyst, UserRole.admin)
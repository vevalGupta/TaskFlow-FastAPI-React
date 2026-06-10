# deps.py
# FastAPI "dependencies" are functions that run before your route handler.
# They handle common logic like auth so you don't repeat it in every route.
#
# Usage:
#   # Any logged-in user
#   def my_route(user: User = Depends(get_current_user)):
#
#   # Only admins
#   def admin_route(user: User = Depends(require_role("admin"))):

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from Backend.core.exceptions import forbidden, unauthorized
from Backend.core.security import decode_access_token
from Backend.DB.Database import get_db
from Backend.Models.model import User

# HTTPBearer extracts the token from the Authorization: Bearer <token> header
bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    1. Check the Authorization header exists
    2. Decode and validate the JWT
    3. Load the user from the database
    4. Attach user to request (returned value is injected into the route)
    """
    if not credentials:
        raise unauthorized("NO_TOKEN", "Authorization header missing")

    # decode_access_token raises ValueError with a code string on failure
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as e:
        code = str(e)
        msg  = "Access token has expired" if code == "TOKEN_EXPIRED" else "Invalid access token"
        raise unauthorized(code, msg)

    # Make sure the user still exists and hasn't been deleted
    user = db.query(User).filter(
        User.id == payload["sub"],
        User.is_deleted.is_(False),
    ).first()

    if not user:
        raise unauthorized("USER_NOT_FOUND", "User account no longer exists")

    return user


def require_role(*roles: str):
    """
    Returns a dependency that only allows users with the given role(s).
    Example: Depends(require_role("admin"))
    """
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise forbidden(f"Role '{current_user.role}' cannot access this resource")
        return current_user
    return _check
# auth/router.py
# HTTP layer for authentication.
# Each function is thin — validate input, call the service, return the response.

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from Backend.api.V1.Auth_dependency import get_current_user
from Backend.core.responses import created, no_content, success
from Backend.core.security import decode_access_token
from Backend.DB.Database import get_db
from Backend.Models.model import User
from Backend.schema.schema import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest
from Backend.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201, summary="Register a new user")
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    """
    Public endpoint — no auth required.
    If a valid admin JWT is present in the header, admin role can be assigned.
    Other-wise role is always forced to "user".
    """
    # Try to find if an admin is making this request (optional auth)
    requesting_user: User | None = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            token   = auth_header.split(" ")[1]
            decoded = decode_access_token(token)
            requesting_user = db.query(User).filter(User.id == decoded["sub"]).first()
        except Exception:
            pass  # not authenticated — that's fine, role will be forced to "user"

    user = auth_service.register(db, payload, requesting_user)
    return created({"user": user}, "Account created successfully", f"/api/v1/users/{user['id']}")


@router.post("/login", summary="Login and receive tokens")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Returns accessToken (15 min) + refreshToken (7 days).
    Store the accessToken in memory; store refreshToken in an httpOnly cookie.
    """
    result = auth_service.login(db, payload)
    return success(result, "Login successful")


@router.post("/refresh", summary="Get a new access token")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """
    Exchange a refresh token for a fresh access + refresh token pair.
    The old refresh token is deleted (rotation).
    """
    result = auth_service.refresh(db, payload)
    return success(result, "Token refreshed")


@router.post("/logout", summary="Invalidate refresh token")
def logout(
    payload: LogoutRequest,
    db:      Session = Depends(get_db),
    _:       User    = Depends(get_current_user),   # requires valid access token
):
    """Deletes the refresh token from the DB so it can't be reused."""
    auth_service.logout(db, payload.refreshToken)
    return no_content()
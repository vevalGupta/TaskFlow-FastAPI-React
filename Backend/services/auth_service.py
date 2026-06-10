# auth_service.py
# Pure business logic for authentication.
# No HTTP knowledge here — no Request, no Response.
# The router calls these functions and handles the HTTP layer.

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from Backend.core.exceptions import conflict, unauthorized
from Backend.core.security import (
    create_access_token, create_refresh_token,
    decode_refresh_token, hash_password, verify_password,
)
from Backend.Models.model import RefreshToken, User
from Backend.schema.schema import LoginRequest, RefreshRequest, RegisterRequest


# ── Helper: format a user object safe to return in a response ─
def _safe_user(user: User) -> dict:
    """Never include password_hash or internal flags in responses."""
    return {
        "id":        user.id,
        "name":      user.name,
        "email":     user.email,
        "role":      user.role,
        "createdAt": user.created_at.isoformat(),
    }


# ── Helper: create both tokens and store the refresh token ────
def _issue_tokens(db: Session, user: User) -> dict:
    access  = create_access_token(user.id, user.role)
    refresh = create_refresh_token(user.id)

    # Store the refresh token in the DB so we can revoke it on logout
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    db.add(RefreshToken(user_id=user.id, token=refresh, expires_at=expires_at))
    db.commit()

    return {"accessToken": access, "refreshToken": refresh, "expiresIn": 900}


# ── Register ──────────────────────────────────────────────────
def register(db: Session, payload: RegisterRequest, requesting_user: User | None) -> dict:
    """
    Create a new user account.
    - Checks the email is not already taken
    - Only an existing admin can create another admin (prevents privilege escalation)
    - Returns a safe user dict (no password hash)
    """
    # Check for duplicate email
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise conflict("EMAIL_TAKEN", "An account with this email already exists")

    # If the request comes from an admin, honor the requested role; otherwise force "user"
    role = payload.role if (requesting_user and requesting_user.role == "admin") else "user"

    user = User(
        name          = payload.name.strip(),
        email         = payload.email.lower(),
        password_hash = hash_password(payload.password),
        role          = role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return _safe_user(user)


# ── Login ─────────────────────────────────────────────────────
def login(db: Session, payload: LoginRequest) -> dict:
    """
    Verify credentials and return access + refresh tokens.
    - We return the same error for wrong email AND wrong password
      so attackers can't enumerate which emails are registered.
    """
    user = db.query(User).filter(
        User.email     == payload.email.lower(),
        User.is_deleted.is_(False),
    ).first()

    # verify_password is always called even if user is None to prevent timing attacks
    if not user or not verify_password(payload.password, user.password_hash):
        raise unauthorized("INVALID_CREDENTIALS", "Invalid email or password")

    tokens = _issue_tokens(db,user)
    return {**tokens, "user": _safe_user(user)}


# ── Refresh ───────────────────────────────────────────────────
def refresh(db: Session, payload: RefreshRequest) -> dict:
    """
    Exchange a refresh token for a new pair of tokens (token rotation).
    - Decodes and validates the JWT
    - Checks the token exists in our DB (not previously used/revoked)
    - Deletes the old token and issues a new one (rotation prevents replay attacks)
    """
    try:
        decoded = decode_refresh_token(payload.refreshToken)
    except ValueError as e:
        raise unauthorized(str(e), "Refresh token is invalid or expired")

    # Check the token is in the DB and not expired
    stored = db.query(RefreshToken).filter(RefreshToken.token == payload.refreshToken).first()
    if not stored or datetime.now(timezone.utc) > stored.expires_at:
        if stored:
            db.delete(stored)
            db.commit()
        raise unauthorized("REFRESH_TOKEN_INVALID", "Refresh token is invalid or expired")

    user = db.query(User).filter(User.id == decoded["sub"], User.is_deleted.is_(False)).first()
    if not user:
        raise unauthorized("USER_NOT_FOUND", "User no longer exists")

    # Delete the used token, then issue a fresh pair
    db.delete(stored)
    db.commit()

    return _issue_tokens(db, user)


# ── Logout ────────────────────────────────────────────────────
def logout(db: Session, refresh_token: str | None) -> None:
    """Delete the stored refresh token so it can never be reused."""
    if refresh_token:
        stored = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        if stored:
            db.delete(stored)
            db.commit()
# users/router.py
# /users/me  → any logged-in user (view + update own profile)
# /users/    → admin only (list all users, change roles, delete)

import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Backend.api.V1.Auth_dependency import get_current_user, require_role
from Backend.core.exceptions import bad_request, not_found
from Backend.core.responses import no_content, success
from Backend.core.security import hash_password
from Backend.DB.Database import get_db
from Backend.Models.model import User
from Backend.schema.schema import RoleUpdateRequest, UpdateMeRequest

router = APIRouter(prefix="/users", tags=["Users"])


def _fmt(user: User) -> dict:
    """Format a user object for API responses — never include password_hash."""
    return {
        "id":        user.id,
        "name":      user.name,
        "email":     user.email,
        "role":      user.role,
        "createdAt": user.created_at.isoformat(),
    }


# ── Own profile ───────────────────────────────────────────────

@router.get("/me", summary="Get my profile")
def get_me(current_user: User = Depends(get_current_user)):
    return success({"user": _fmt(current_user)})


@router.patch("/me", summary="Update my name or password")
def update_me(
    payload:      UpdateMeRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    if payload.name:
        current_user.name = payload.name.strip()
    if payload.password:
        current_user.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(current_user)
    return success({"user": _fmt(current_user)}, "Profile updated")


# ── Admin: manage all users ───────────────────────────────────

@router.get("/", summary="List all users (admin only)")
def list_users(
    page:  int = Query(1,  ge=1),
    limit: int = Query(20, ge=1, le=100),
    db:    Session = Depends(get_db),
    _:     User    = Depends(require_role("admin")),
):
    query = db.query(User).filter(User.is_deleted.is_(False))
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return success(
        {"users": [_fmt(u) for u in users]},
        "Users retrieved",
        meta={
            "total":      total,
            "page":       page,
            "limit":      limit,
            "totalPages": math.ceil(total / limit) if total else 1,
        },
    )


@router.patch("/{user_id}/role", summary="Change a user's role (admin only)")
def update_role(
    user_id: str,
    payload: RoleUpdateRequest,
    db:      Session = Depends(get_db),
    _:       User    = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first()
    if not user:
        raise not_found("User not found")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return success({"user": _fmt(user)}, "Role updated")


@router.delete("/{user_id}", status_code=204, summary="Delete a user (admin only)")
def delete_user(
    user_id:      str,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(require_role("admin")),
):
    if user_id == current_user.id:
        raise bad_request("You cannot delete your own account")

    user = db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first()
    if not user:
        raise not_found("User not found")

    user.is_deleted = True   # soft delete
    db.commit()
    return no_content()
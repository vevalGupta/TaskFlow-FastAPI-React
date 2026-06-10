# schemas.py
# Pydantic models define what data goes IN (request body)
# and what comes OUT (response body).
#
# FastAPI uses these for:
#   - Automatic request validation
#   - Auto-generated Swagger docs
#   - Serializing ORM objects to JSON

from __future__ import annotations
import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# OrmBase lets Pydantic read SQLAlchemy ORM objects directly
# (e.g. UserOut.model_validate(db_user))
class OrmBase(BaseModel):
    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ══════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    name:     str      = Field(..., min_length=2, max_length=80)
    email:    EmailStr
    password: str      = Field(..., min_length=8, max_length=128)
    role:     Literal["user", "admin"] = "user"

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Must contain at least one number")
        if not re.search(r"[^a-zA-Z0-9]", v):
            raise ValueError("Must contain at least one special character")
        return v


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    refreshToken: str


class LogoutRequest(BaseModel):
    refreshToken: Optional[str] = None


# ══════════════════════════════════════════════════════════════
# USER SCHEMAS
# ══════════════════════════════════════════════════════════════

class UserOut(OrmBase):
    id:         str
    name:       str
    email:      str
    role:       str
    created_at: datetime


class UpdateMeRequest(BaseModel):
    name:     Optional[str] = Field(None, min_length=2, max_length=80)
    password: Optional[str] = Field(None, min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Must contain at least one number")
        if not re.search(r"[^a-zA-Z0-9]", v):
            raise ValueError("Must contain at least one special character")
        return v

    # At least one of name or password must be provided
    @model_validator(mode="after")
    def at_least_one_field(self) -> "UpdateMeRequest":
        if self.name is None and self.password is None:
            raise ValueError("Provide at least one field to update")
        return self


class RoleUpdateRequest(BaseModel):
    role: Literal["user", "admin"]


# ══════════════════════════════════════════════════════════════
# TASK SCHEMAS
# ══════════════════════════════════════════════════════════════

class TaskCreate(BaseModel):
    title:       str            = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status:      Literal["todo", "in_progress", "done"] = "todo"
    priority:    Literal["low", "medium", "high"]        = "medium"
    due_date:    Optional[str]  = None    # expected format: "YYYY-MM-DD"

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        return v.strip()

    @field_validator("due_date")
    @classmethod
    def valid_date_format(cls, v: str | None) -> str | None:
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Due date must be in YYYY-MM-DD format")
        return v


class TaskUpdate(BaseModel):
    """Partial update — all fields optional, but at least one required."""
    title:       Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status:      Optional[Literal["todo", "in_progress", "done"]] = None
    priority:    Optional[Literal["low", "medium", "high"]]        = None
    due_date:    Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "TaskUpdate":
        if all(v is None for v in [self.title, self.description, self.status, self.priority, self.due_date]):
            raise ValueError("Provide at least one field to update")
        return self


class TaskOut(OrmBase):
    id:          str
    user_id:     str
    title:       str
    description: Optional[str]
    status:      str
    priority:    str
    due_date:    Optional[str]
    created_at:  datetime
    updated_at:  datetime
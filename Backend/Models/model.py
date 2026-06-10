# models.py
# SQLAlchemy ORM models — each class maps to a database table.
# Columns are declared as class attributes.
# Relationships let you navigate between tables in Python (user.tasks).

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from Backend.DB.Database import Base


def _uuid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── User ──────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id            = Column(String(36),  primary_key=True, default=_uuid)
    name          = Column(String(80),  nullable=False)
    email         = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # role can only be "user" or "admin"
    role          = Column(Enum("user", "admin", name="user_role"), nullable=False, default="user")

    # Soft delete — we never permanently remove users, just mark them deleted
    is_deleted    = Column(Boolean, nullable=False, default=False)

    created_at    = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at    = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    # One user → many tasks
    tasks          = relationship("Task",         back_populates="user", lazy="dynamic")
    # One user → many refresh tokens (one per device/login)
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


# ── Task ──────────────────────────────────────────────────────
class Task(Base):
    __tablename__ = "tasks"

    id          = Column(String(36),  primary_key=True, default=_uuid)
    user_id     = Column(String(36),  ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title       = Column(String(255), nullable=False)
    description = Column(Text,        nullable=True)

    status      = Column(Enum("todo", "in_progress", "done",  name="task_status"),   nullable=False, default="todo")
    priority    = Column(Enum("low",  "medium",      "high",  name="task_priority"), nullable=False, default="medium")

    due_date    = Column(String(10),  nullable=True)    # stored as "YYYY-MM-DD"
    is_deleted  = Column(Boolean,     nullable=False, default=False)

    created_at  = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at  = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    # Each task belongs to one user
    user = relationship("User", back_populates="tasks")


# ── RefreshToken ──────────────────────────────────────────────
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id         = Column(String(36),  primary_key=True, default=_uuid)
    user_id    = Column(String(36),  ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token      = Column(String(512), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
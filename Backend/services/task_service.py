# task_service.py
# All task business logic lives here.
# Key rule: users can only see/edit their own tasks.
#           admins can see/edit all tasks.

import math

from sqlalchemy.orm import Session

from Backend.core.exceptions import forbidden, not_found
from Backend.Models.model import Task, User
from Backend.schema.schema import TaskCreate, TaskUpdate


# ── Ownership check ───────────────────────────────────────────
def _assert_access(task: Task, user: User) -> None:
    """Raise 403 if a regular user tries to touch someone else's task."""
    if user.role != "admin" and task.user_id != user.id:
        raise forbidden("You do not have access to this task")


# ── List ──────────────────────────────────────────────────────
def list_tasks(
    db:       Session,
    user:     User,
    page:     int,
    limit:    int,
    status:   str | None,
    priority: str | None,
) -> tuple[list[Task], dict]:
    """
    Returns (tasks, pagination_meta).
    Admins see all tasks; regular users only see their own.
    """
    query = db.query(Task).filter(Task.is_deleted.is_(False))

    # Scope to current user unless admin
    if user.role != "admin":
        query = query.filter(Task.user_id == user.id)

    # Optional filters
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    meta = {
        "total":      total,
        "page":       page,
        "limit":      limit,
        "totalPages": math.ceil(total / limit) if total else 1,
    }
    return tasks, meta


# ── Get one ───────────────────────────────────────────────────
def get_task(db: Session, task_id: str, user: User) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted.is_(False)).first()
    if not task:
        raise not_found("Task not found")
    _assert_access(task, user)
    return task


# ── Create ────────────────────────────────────────────────────
def create_task(db: Session, payload: TaskCreate, user: User) -> Task:
    task = Task(user_id=user.id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# ── Update (full or partial) ──────────────────────────────────
def update_task(db: Session, task_id: str, payload: TaskUpdate, user: User) -> Task:
    task = get_task(db, task_id, user)

    # model_dump(exclude_unset=True) only returns fields the caller actually sent
    # so a PATCH with just {"status": "done"} won't wipe the title
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


# ── Delete (soft) ─────────────────────────────────────────────
def delete_task(db: Session, task_id: str, user: User) -> None:
    """Mark as deleted — never actually removes the row."""
    task = get_task(db, task_id, user)
    task.is_deleted = True
    db.commit()
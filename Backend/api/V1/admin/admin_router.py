# admin/router.py
# Admin-only endpoints.
# All routes use require_role("admin") so a regular user gets 403.

import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from Backend.api.V1.Auth_dependency import require_role
from Backend.core.responses import success
from Backend.DB.Database import get_db
from Backend.Models.model import Task, User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", summary="System-wide statistics")
def dashboard(
    db: Session = Depends(get_db),
    _:  User    = Depends(require_role("admin")),
):
    """Returns total user count, total task count, and tasks broken down by status."""
    total_users = db.query(User).filter(User.is_deleted.is_(False)).count()
    total_tasks = db.query(Task).filter(Task.is_deleted.is_(False)).count()

    # GROUP BY status to get counts per status in one query
    rows = (
        db.query(Task.status, func.count(Task.id))
        .filter(Task.is_deleted.is_(False))
        .group_by(Task.status)
        .all()
    )
    tasks_by_status = {"todo": 0, "in_progress": 0, "done": 0}
    for status, count in rows:
        tasks_by_status[status] = count

    return success({
        "stats": {
            "totalUsers":    total_users,
            "totalTasks":    total_tasks,
            "tasksByStatus": tasks_by_status,
        }
    })


@router.get("/tasks", summary="All tasks across all users")
def all_tasks(
    page:  int = Query(1,  ge=1),
    limit: int = Query(20, ge=1, le=100),
    db:    Session = Depends(get_db),
    _:     User    = Depends(require_role("admin")),
):
    """
    Returns every task with the owner's info joined in.
    joined-load avoids N+1 queries (one query instead of one per task).
    """
    query = (
        db.query(Task)
        .options(joinedload(Task.user))
        .filter(Task.is_deleted.is_(False))
    )
    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    data = [
        {
            "id":        t.id,
            "title":     t.title,
            "status":    t.status,
            "priority":  t.priority,
            "dueDate":   t.due_date,
            "createdAt": t.created_at.isoformat(),
            # Include the owner so admins can see who created each task
            "user": {
                "id":    t.user.id,
                "name":  t.user.name,
                "email": t.user.email,
            } if t.user else None,
        }
        for t in tasks
    ]

    return success(
        {"tasks": data},
        "All tasks retrieved",
        meta={
            "total":      total,
            "page":       page,
            "limit":      limit,
            "totalPages": math.ceil(total / limit) if total else 1,
        },
    )
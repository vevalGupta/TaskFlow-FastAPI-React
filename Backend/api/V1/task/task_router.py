# tasks/router.py
# Full CRUD for tasks.
# All routes require a valid JWT (get_current_user).
# The service layer handles ownership checks.

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Backend.api.V1.Auth_dependency import get_current_user
from Backend.core.responses import created, no_content, success
from Backend.DB.Database import get_db
from Backend.Models.model import Task, User
from Backend.schema.schema import TaskCreate, TaskUpdate
from Backend.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _fmt(task: Task) -> dict:
    return {
        "id":          task.id,
        "userId":      task.user_id,
        "title":       task.title,
        "description": task.description,
        "status":      task.status,
        "priority":    task.priority,
        "dueDate":     task.due_date,
        "createdAt":   task.created_at.isoformat(),
        "updatedAt":   task.updated_at.isoformat(),
    }


@router.get("/", summary="List my tasks")
def list_tasks(
    page:     int           = Query(1,  ge=1),
    limit:    int           = Query(20, ge=1, le=100),
    status:   Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db:       Session       = Depends(get_db),
    user:     User          = Depends(get_current_user),
):
    tasks, meta = task_service.list_tasks(db, user, page, limit, status, priority)
    return success({"tasks": [_fmt(t) for t in tasks]}, "Tasks retrieved", meta=meta)


@router.post("/", status_code=201, summary="Create a task")
def create_task(
    payload: TaskCreate,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    task = task_service.create_task(db, payload, user)
    return created({"task": _fmt(task)}, "Task created", f"/api/v1/tasks/{task.id}")


@router.get("/{task_id}", summary="Get a single task")
def get_task(
    task_id: str,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    task = task_service.get_task(db, task_id, user)
    return success({"task": _fmt(task)})


@router.put("/{task_id}", summary="Replace a task (full update)")
def replace_task(
    task_id: str,
    payload: TaskCreate,   # full payload required for PUT
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    # Reuse update_task with all fields set
    update_payload = TaskUpdate(**payload.model_dump())
    task = task_service.update_task(db, task_id, update_payload, user)
    return success({"task": _fmt(task)}, "Task updated")


@router.patch("/{task_id}", summary="Update a task (partial update)")
def update_task(
    task_id: str,
    payload: TaskUpdate,   # all fields optional for PATCH
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    task = task_service.update_task(db, task_id, payload, user)
    return success({"task": _fmt(task)}, "Task updated")


@router.delete("/{task_id}", status_code=204, summary="Delete a task")
def delete_task(
    task_id: str,
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    task_service.delete_task(db, task_id, user)
    return no_content()
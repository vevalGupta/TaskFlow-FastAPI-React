# router.py
# One place that registers all v1 routes.
# main.py only needs to include this single router.

from fastapi import APIRouter

from Backend.api.V1.auth.auth_router  import router as auth_router
from Backend.api.V1.user.user_router import router as users_router
from Backend.api.V1.task.task_router import router as tasks_router
from Backend.api.V1.admin.admin_router import router as admin_router

# All routes will be prefixed with /api/v1
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(tasks_router)
api_router.include_router(admin_router)
# main.py
# The entry point of the application.
# This is where FastAPI is created and configured:
#   - CORS (which frontend origins can call the API)
#   - Global error handlers (so every error returns the same shape)
#   - Route registration
#   - Database table creation on startup

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from Backend.api.V1.sub_rout import api_router
from Backend.core.config import settings
from Backend.core.exceptions import AppError
from Backend.DB.Database import Base, engine
from Backend.Models import model  # noqa — import models so SQLAlchemy registers them


# ── Startup / shutdown ────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables that don't exist yet on startup
    # In production, use Alembic migrations instead
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready")
    yield
    print("Server shutting down")


# ── Create app ────────────────────────────────────────────────
app = FastAPI(
    title="TaskFlow API",
    version="1.0.0",
    description="REST API with JWT auth and role-based access control",
    docs_url="/api/docs",      # Swagger UI
    redoc_url="/api/redoc",    # ReDoc
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────
# Allow the React frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Error handlers ────────────────────────────────────────────
# These catch errors thrown anywhere in the app and format them
# into our standard { success: false, error: { code, message } } shape

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Handles errors raised with our custom raise unauthorized/not_found/etc helpers."""
    detail = exc.detail
    body = {
        "success": False,
        "error": {
            "code":    detail["code"],
            "message": detail["message"],
        },
    }
    # Include field-level errors if present (e.g. from validation_error())
    if detail.get('fields'):
        body["error"]["fields"] = detail['fields']
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(ValidationError)
async def pydantic_error_handler(request: Request, exc: ValidationError):
    """Handles Pydantic validation errors — turns them into our field-level error shape."""
    fields = {}
    for e in exc.errors():
        # e["loc"] is like ("body", "email") — join to get "email"
        key = ".".join(str(p) for p in e["loc"] if p != "body")
        fields[key] = e["msg"].replace("Value error, ", "")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code":    "VALIDATION_ERROR",
                "message": "Request validation failed",
                "fields":  fields,
            },
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors — never expose stack traces in production."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code":    "INTERNAL_ERROR",
                "message": str(exc) if settings.DEBUG else "Something went wrong",
            },
        },
    )


# ── Routes ────────────────────────────────────────────────────
app.include_router(api_router)


# Health check — useful for load balancers and uptime monitors
@app.get("/health", tags=["Health"])
def health():
    from datetime import datetime, timezone
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
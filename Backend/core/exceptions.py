# exceptions.py
# Helper functions that create HTTP errors with a consistent
# { code, message, fields } shape.
#
# Usage:
#   raise not_found("Task not found")
#   raise unauthorized("TOKEN_EXPIRED", "Access token has expired")

from fastapi import HTTPException


class AppError(HTTPException):
    """Our base error class — adds a short machine-readable `code`."""
    def __init__(self, status_code: int, code: str, message: str, fields: dict | None = None):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "fields": fields},
        )


# ── Shortcuts ─────────────────────────────────────────────────

def bad_request(message: str = "Bad request", fields: dict | None = None) -> AppError:
    return AppError(400, "BAD_REQUEST", message, fields)

def unauthorized(code: str = "UNAUTHORIZED", message: str = "Authentication required") -> AppError:
    return AppError(401, code, message)

def forbidden(message: str = "Access denied") -> AppError:
    return AppError(403, "FORBIDDEN", message)

def not_found(message: str = "Resource not found") -> AppError:
    return AppError(404, "NOT_FOUND", message)

def conflict(code: str = "CONFLICT", message: str = "Conflict") -> AppError:
    return AppError(409, code, message)

def validation_error(fields: dict) -> AppError:
    return AppError(422, "VALIDATION_ERROR", "Request validation failed", fields)
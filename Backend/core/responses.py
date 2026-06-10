# responses.py
# Every API response uses the same shape so the frontend
# can always read .success, .data, .error without guessing.
#
# Success shape:  { success: true,  message: "...", data: {...}, meta?: {...}}
# Error shape:    { success: false, error: { code: "...", message: "...", fields?: {...}}}

from typing import Any
from fastapi.responses import JSONResponse


def success(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    meta: dict | None = None,
) -> JSONResponse:
    body = {"success": True, "message": message, "data": data}
    if meta:
        body["meta"] = meta
    return JSONResponse(content=body, status_code=status_code)


def created(
    data: Any,
    message: str = "Created successfully",
    location: str | None = None,
) -> JSONResponse:
    headers = {"Location": location} if location else {}
    return JSONResponse(
        content={"success": True, "message": message, "data": data},
        status_code=201,
        headers=headers,
    )


def no_content() -> JSONResponse:
    return JSONResponse(content=None, status_code=204)


def error(
    code: str,
    message: str,
    status_code: int,
    fields: dict | None = None,
) -> JSONResponse:
    body: dict = {"success": False, "error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = fields
    return JSONResponse(content=body, status_code=status_code)
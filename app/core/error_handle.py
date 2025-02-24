import logging
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .i18n import _

logger = logging.getLogger(__name__)

class AuthorizationException(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg

def create_error_response(
    status_code: int, code: int, msg: str, details: Dict[str, Any] = None
) -> JSONResponse:
    """Helper function to create a standardized error response."""
    content = {"code": code, "msg": msg}
    if details:
        content["details"] = details
    return JSONResponse(status_code=status_code, content=content)

def register_exception(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI app."""

    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handler(
        request: Request, exc: AuthorizationException
    ) -> JSONResponse:
        return create_error_response(status_code=401, code=exc.code, msg=exc.msg)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        exc_str = f'{exc}'.replace('\n','').replace('   ','')
        logging.error(f"Validation error: {request.url}, {request.headers}, {exc_str}")
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=10002,
            msg=_("Invalid request body"),
            details={"exc": exc_str},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        logging.error(f"HTTP exception: {request.url}, {request.headers}, {exc}")
        return create_error_response(
            status_code=exc.status_code, code=exc.status_code, msg=exc.detail
        )

    @app.exception_handler(AssertionError)
    async def assertion_exception_handler(
        request: Request, exc: AssertionError
    ) -> JSONResponse:
        logging.error(f"Assertion error: {request.url}, {request.headers}, {exc}")
        status_code = exc.args[0] if exc.args else status.HTTP_500_INTERNAL_SERVER_ERROR
        return create_error_response(
            status_code=status_code,
            code=500,
            msg="Assertion failed",
            details={"tip": "Server error"},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logging.error(f"Global exception: {request.url}, {request.headers}, {exc}")
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=500,
            msg="Internal server error",
            details={"tip": "Server error"},
        )
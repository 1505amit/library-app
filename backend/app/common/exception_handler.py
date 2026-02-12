"""
Global exception handlers for converting domain exceptions to HTTP responses.
Centralizes all error handling logic in one place.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.common.exceptions import (
    AppException,
    BookNotFoundError,
    InvalidBookError,
    DatabaseError,
    MemberNotFoundError,
    InvalidMemberError,
    BorrowNotFoundError,
    InvalidBorrowError,
)
import logging

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Convert domain exceptions to HTTP responses.

    Maps application exceptions to appropriate HTTP status codes:
    - NotFound errors → 404
    - Invalid errors → 400
    - Database errors → 500
    - Unknown errors → 500
    """

    # 404 Not Found errors
    if isinstance(exc, (BookNotFoundError, MemberNotFoundError, BorrowNotFoundError)):
        logger.error(f"Resource not found: {exc}")
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

    # 400 Bad Request errors
    if isinstance(exc, (InvalidBookError, InvalidMemberError, InvalidBorrowError)):
        logger.error(f"Invalid data: {exc}")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    # 500 Server errors
    if isinstance(exc, DatabaseError):
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Database operation failed. Please try again later."}
        )

    # Unknown AppException
    if isinstance(exc, AppException):
        logger.error(f"Unexpected application error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred. Please try again later."}
        )

    # Unknown error - should reach here only if an unhandled exception type is raised
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def add_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    app.add_exception_handler(AppException, app_exception_handler)

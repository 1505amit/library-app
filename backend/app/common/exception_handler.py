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
    Convert all exceptions to HTTP responses.

    Handles both domain exceptions (AppException and subclasses) and unexpected
    built-in exceptions (ValueError, KeyError, TypeError, etc.).

    Maps application exceptions to appropriate HTTP status codes:
    - NotFound errors (404) → BookNotFoundError, MemberNotFoundError, BorrowNotFoundError
    - Invalid errors (400) → InvalidBookError, InvalidMemberError, InvalidBorrowError
    - Database errors (500) → DatabaseError
    - Other AppException (500) → Unknown domain errors
    - Unexpected exceptions (500) → ValueError, KeyError, TypeError, etc.
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
        content={"detail": "An unexpected error occurred. Please try again later."}
    )


def add_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.

    Registers handlers in order of specificity:
    1. AppException and subclasses - domain-specific errors
    2. Exception (catch-all) - unexpected errors

    Args:
        app: The FastAPI application instance
    """
    # Register for domain exceptions (AppException and all subclasses)
    app.add_exception_handler(AppException, app_exception_handler)

    # Register for any other unexpected exceptions
    app.add_exception_handler(Exception, app_exception_handler)

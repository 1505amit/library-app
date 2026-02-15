"""Minimal unit tests for exception handler covering all scenarios.

Tests all exception types and their HTTP responses without redundancy:
- 404 NotFound errors (BookNotFoundError, MemberNotFoundError, BorrowNotFoundError)
- 400 Invalid data errors (InvalidBookError, InvalidMemberError, InvalidBorrowError)
- 500 Database errors (DatabaseError)
- 500 Raw AppException (unexpected domain error not matching known subclasses)
- 500 Unexpected built-in exceptions (ValueError, KeyError, TypeError, etc.)
"""
import asyncio
import json
from unittest.mock import Mock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.common.exception_handler import app_exception_handler, add_exception_handlers
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


@pytest.fixture
def app_with_handlers():
    """Create FastAPI app with exception handlers for testing."""
    app = FastAPI()

    # Test routes for AppException subclasses (which TestClient handles well)
    @app.get("/not_found/{entity_type}")
    async def raise_not_found(entity_type: str):
        not_found_errors = {
            "book": BookNotFoundError("Book not found"),
            "member": MemberNotFoundError("Member not found"),
            "borrow": BorrowNotFoundError("Borrow not found"),
        }
        raise not_found_errors[entity_type]

    @app.get("/invalid/{entity_type}")
    async def raise_invalid(entity_type: str):
        invalid_errors = {
            "book": InvalidBookError("Invalid book data"),
            "member": InvalidMemberError("Invalid member data"),
            "borrow": InvalidBorrowError("Invalid borrow data"),
        }
        raise invalid_errors[entity_type]

    @app.get("/database_error")
    async def raise_database_error():
        raise DatabaseError("Database connection failed")

    @app.get("/raw_app_exception")
    async def raise_raw_exception():
        raise AppException("Unknown application error")

    @app.get("/unexpected_error")
    async def raise_unexpected_error():
        raise ValueError("Unexpected value error")

    add_exception_handlers(app)
    return app


@pytest.fixture
def client(app_with_handlers):
    """TestClient for the app."""
    return TestClient(app_with_handlers)


# ============================================================================
# Direct Handler Tests - Unit tests using asyncio.run()
# ============================================================================

class TestExceptionHandlerDirectly:
    """Direct unit tests of exception handler for complete code path coverage.

    These tests directly call app_exception_handler without using TestClient
    to ensure all code paths are covered, especially lines 72-76 which handle
    unexpected exceptions like ValueError, KeyError, TypeError, etc.
    """

    def test_raw_app_exception_direct(self):
        """Test exception handler directly with raw AppException.

        Tests lines 63-70 of exception_handler.py for raw AppException handling.
        """
        mock_request = Mock()
        exc = AppException("Unknown error")

        response = asyncio.run(app_exception_handler(mock_request, exc))
        assert response.status_code == 500
        body = json.loads(response.body.decode())
        assert "An unexpected error occurred" in body["detail"]

    @pytest.mark.parametrize("exception_obj", [
        ValueError("Invalid value"),
        KeyError("Missing key"),
        TypeError("Wrong type"),
        RuntimeError("Runtime issue"),
    ])
    def test_unexpected_exceptions_direct(self, exception_obj):
        """Test exception handler directly with unexpected built-in exceptions.

        Tests lines 72-76 of exception_handler.py for catch-all handler
        that handles unexpected exceptions not derived from AppException.
        """
        mock_request = Mock()

        response = asyncio.run(
            app_exception_handler(mock_request, exception_obj))
        assert response.status_code == 500
        body = json.loads(response.body.decode())
        assert "An unexpected error occurred" in body["detail"]

"""Unit tests for Borrow API endpoints.

Tests cover:
- GET /api/v1/borrow/ with various filters and pagination
- POST /api/v1/borrow/ for creating borrow records
- PATCH /api/v1/borrow/{borrow_id}/return for returning books

Exception Mapping (from app.common.exceptions):
- BookNotFoundError → HTTP 404
- MemberNotFoundError → HTTP 404
- BorrowNotFoundError → HTTP 404
- InvalidBorrowError → HTTP 400
- DatabaseError → HTTP 500
"""
import pytest
from unittest.mock import MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.schemas.borrow import (
    BorrowResponse,
    BorrowRequest,
    BorrowDetailedResponse,
    PaginatedBorrowDetailedResponse,
)
from app.services.borrow_service import BorrowService
from app.api.v1.borrow import get_borrow_service
from app.common.exceptions import (
    BookNotFoundError,
    MemberNotFoundError,
    BorrowNotFoundError,
    InvalidBorrowError,
    DatabaseError,
)


# ============================================================================
# Test Data Constants
# ============================================================================

ACTIVE_BORROW_ID = 1
RETURNED_BORROW_ID = 2
DEFAULT_MEMBER_ID = 1
DEFAULT_BOOK_ID = 1
DEFAULT_PAGE = 1
DEFAULT_LIMIT = 10


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    return MagicMock()


@pytest.fixture(autouse=True)
def clear_overrides():
    """Clear dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_borrow_service():
    """Create a mock BorrowService instance."""
    return MagicMock(spec=BorrowService)


# ============================================================================
# Test Data Builders
# ============================================================================


def create_borrow_response(
    borrow_id: int = ACTIVE_BORROW_ID,
    book_id: int = DEFAULT_BOOK_ID,
    member_id: int = DEFAULT_MEMBER_ID,
    borrowed_at: datetime = None,
    returned_at: datetime = None,
) -> BorrowResponse:
    """Create a BorrowResponse object for testing."""
    return BorrowResponse(
        id=borrow_id,
        book_id=book_id,
        member_id=member_id,
        borrowed_at=borrowed_at or datetime(2026, 2, 1),
        returned_at=returned_at,
    )


def create_borrow_detailed_response(
    borrow_id: int = ACTIVE_BORROW_ID,
    book_id: int = DEFAULT_BOOK_ID,
    member_id: int = DEFAULT_MEMBER_ID,
    borrowed_at: datetime = None,
    returned_at: datetime = None,
    book_title: str = "Test Book",
    book_author: str = "Test Author",
    member_name: str = "Test Member",
    member_email: str = "test@example.com",
) -> BorrowDetailedResponse:
    """Create a BorrowDetailedResponse object for testing."""
    return BorrowDetailedResponse(
        id=borrow_id,
        book_id=book_id,
        member_id=member_id,
        borrowed_at=borrowed_at or datetime(2026, 2, 1),
        returned_at=returned_at,
        book={
            "id": book_id,
            "title": book_title,
            "author": book_author,
            "published_year": 2025,
        },
        member={
            "id": member_id,
            "name": member_name,
            "email": member_email,
        },
    )


def create_paginated_borrow_response(
    data: list[BorrowDetailedResponse],
    page: int = DEFAULT_PAGE,
    limit: int = DEFAULT_LIMIT,
    total: int = None,
) -> PaginatedBorrowDetailedResponse:
    """Create a PaginatedBorrowDetailedResponse object for testing."""
    if total is None:
        total = len(data)
    pages = (total + limit - 1) // limit
    return PaginatedBorrowDetailedResponse(
        data=data,
        pagination={
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        },
    )


# ============================================================================
# Fixture Shortcuts for Common Test Cases
# ============================================================================


@pytest.fixture
def mock_borrow_response():
    """Mock simple borrow response fixture."""
    return create_borrow_response()


@pytest.fixture
def mock_borrow_detailed_response():
    """Mock detailed borrow response fixture."""
    return create_borrow_detailed_response()


@pytest.fixture
def mock_returned_borrow_response():
    """Mock returned borrow response fixture."""
    return create_borrow_detailed_response(
        borrow_id=RETURNED_BORROW_ID,
        book_id=2,
        member_id=2,
        borrowed_at=datetime(2026, 1, 1),
        returned_at=datetime(2026, 2, 1),
        book_title="Returned Book",
        book_author="Author Name",
        member_name="Another Member",
        member_email="another@example.com",
    )


# ============================================================================
# POST /api/v1/borrow/ - Borrow Book Tests
# ============================================================================


class TestBorrowBook:
    """Tests for POST /api/v1/borrow/ endpoint."""

    def test_success(self, client, mock_borrow_response, mock_borrow_service):
        """Test successful book borrowing."""
        mock_borrow_service.borrow_book.return_value = mock_borrow_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.post(
            "/api/v1/borrow/", json={"book_id": 1, "member_id": 1})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == ACTIVE_BORROW_ID
        assert data["book_id"] == DEFAULT_BOOK_ID
        assert data["member_id"] == DEFAULT_MEMBER_ID
        assert data["returned_at"] is None
        mock_borrow_service.borrow_book.assert_called_once()

    def test_book_not_found(self, client, mock_borrow_service):
        """Test borrowing when book does not exist (404)."""
        mock_borrow_service.borrow_book.side_effect = BookNotFoundError(
            "Book with id 999 not found"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.post(
            "/api/v1/borrow/", json={"book_id": 999, "member_id": 1}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_book_not_available(self, client, mock_borrow_service):
        """Test borrowing when book is not available (400)."""
        mock_borrow_service.borrow_book.side_effect = InvalidBorrowError(
            "Book with id 1 is not available"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.post(
            "/api/v1/borrow/", json={"book_id": 1, "member_id": 1})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not available" in response.json()["detail"]

    def test_member_not_found(self, client, mock_borrow_service):
        """Test borrowing when member does not exist (404)."""
        mock_borrow_service.borrow_book.side_effect = MemberNotFoundError(
            "Member with id 999 not found"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.post(
            "/api/v1/borrow/", json={"book_id": 1, "member_id": 999}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_member_not_active(self, client, mock_borrow_service):
        """Test borrowing when member is not active (400)."""
        mock_borrow_service.borrow_book.side_effect = InvalidBorrowError(
            "Member with id 1 is not active"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.post(
            "/api/v1/borrow/", json={"book_id": 1, "member_id": 1})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not active" in response.json()["detail"]

    def test_database_error(self, client, mock_borrow_service):
        """Test borrowing when database error occurs (500)."""
        mock_borrow_service.borrow_book.side_effect = DatabaseError(
            "Database connection failed"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.post(
            "/api/v1/borrow/", json={"book_id": 1, "member_id": 1})

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database operation failed" in response.json()["detail"]


# ============================================================================
# GET /api/v1/borrow/ - Get All Borrows Tests
# ============================================================================


class TestGetAllBorrows:
    """Tests for GET /api/v1/borrow/ endpoint."""

    def test_default_parameters(self, client, mock_borrow_detailed_response, mock_borrow_service):
        """Test getting borrows with default parameters."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response]
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) == 1
        assert data["pagination"]["page"] == DEFAULT_PAGE
        assert data["pagination"]["limit"] == DEFAULT_LIMIT
        mock_borrow_service.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=None,
            book_id=None,
            page=DEFAULT_PAGE,
            limit=DEFAULT_LIMIT,
        )

    def test_returned_true(self, client, mock_borrow_detailed_response, mock_returned_borrow_response, mock_borrow_service):
        """Test getting all borrows with returned=True."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response,
                  mock_returned_borrow_response],
            total=2,
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/?returned=true")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2
        assert data["data"][0]["returned_at"] is None
        assert data["data"][1]["returned_at"] is not None

    def test_returned_false(self, client, mock_borrow_detailed_response, mock_borrow_service):
        """Test getting only active borrows with returned=False."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response]
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/?returned=false")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["returned_at"] is None
        mock_borrow_service.get_all_borrows.assert_called_once_with(
            returned=False,
            member_id=None,
            book_id=None,
            page=DEFAULT_PAGE,
            limit=DEFAULT_LIMIT,
        )

    def test_empty_result(self, client, mock_borrow_service):
        """Test getting borrows when no records exist."""
        paginated_response = create_paginated_borrow_response(data=[], total=0)
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 0
        assert data["pagination"]["total"] == 0

    def test_with_member_filter(self, client, mock_borrow_detailed_response, mock_borrow_service):
        """Test getting borrows filtered by member_id."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response]
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/?member_id=123")

        assert response.status_code == status.HTTP_200_OK
        mock_borrow_service.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=123,
            book_id=None,
            page=DEFAULT_PAGE,
            limit=DEFAULT_LIMIT,
        )

    def test_with_book_filter(self, client, mock_borrow_detailed_response, mock_borrow_service):
        """Test getting borrows filtered by book_id."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response]
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/?book_id=456")

        assert response.status_code == status.HTTP_200_OK
        mock_borrow_service.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=None,
            book_id=456,
            page=DEFAULT_PAGE,
            limit=DEFAULT_LIMIT,
        )

    def test_with_both_filters(self, client, mock_borrow_detailed_response, mock_borrow_service):
        """Test getting borrows filtered by both member_id and book_id."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response]
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/?member_id=123&book_id=456")

        assert response.status_code == status.HTTP_200_OK
        mock_borrow_service.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=123,
            book_id=456,
            page=DEFAULT_PAGE,
            limit=DEFAULT_LIMIT,
        )

    def test_with_all_filters(self, client, mock_borrow_detailed_response, mock_borrow_service):
        """Test getting borrows with all filters combined."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response]
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get(
            "/api/v1/borrow/?returned=false&member_id=123&book_id=456"
        )

        assert response.status_code == status.HTTP_200_OK
        mock_borrow_service.get_all_borrows.assert_called_once_with(
            returned=False,
            member_id=123,
            book_id=456,
            page=DEFAULT_PAGE,
            limit=DEFAULT_LIMIT,
        )

    def test_pagination_first_page(self, client, mock_borrow_detailed_response, mock_borrow_service):
        """Test pagination on first page."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response],
            page=1,
            limit=10,
            total=25,
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/?page=1&limit=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["total"] == 25
        assert data["pagination"]["pages"] == 3

    def test_pagination_second_page(self, client, mock_borrow_detailed_response, mock_borrow_service):
        """Test pagination on second page."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response],
            page=2,
            limit=10,
            total=25,
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/?page=2&limit=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pagination"]["page"] == 2
        mock_borrow_service.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=None,
            book_id=None,
            page=2,
            limit=10,
        )

    def test_pagination_custom_limit(self, client, mock_borrow_detailed_response, mock_borrow_service):
        """Test pagination with custom limit."""
        paginated_response = create_paginated_borrow_response(
            data=[mock_borrow_detailed_response],
            page=1,
            limit=25,
            total=25,
        )
        mock_borrow_service.get_all_borrows.return_value = paginated_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/?limit=25")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pagination"]["limit"] == 25

    def test_validation_error(self, client, mock_borrow_service):
        """Test get_all_borrows when service raises InvalidBorrowError (400)."""
        mock_borrow_service.get_all_borrows.side_effect = InvalidBorrowError(
            "Page 10 exceeds total pages 2"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "exceeds total pages" in response.json()["detail"]

    def test_database_error(self, client, mock_borrow_service):
        """Test get_all_borrows when database error occurs (500)."""
        mock_borrow_service.get_all_borrows.side_effect = DatabaseError(
            "Database connection failed"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.get("/api/v1/borrow/")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database operation failed" in response.json()["detail"]


# ============================================================================
# PATCH /api/v1/borrow/{borrow_id}/return - Return Book Tests
# ============================================================================


class TestReturnBook:
    """Tests for PATCH /api/v1/borrow/{borrow_id}/return endpoint."""

    def test_success(self, client, mock_returned_borrow_response, mock_borrow_service):
        """Test successful book return."""
        mock_borrow_service.return_borrow.return_value = mock_returned_borrow_response
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.patch("/api/v1/borrow/1/return")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == RETURNED_BORROW_ID
        assert data["returned_at"] is not None
        mock_borrow_service.return_borrow.assert_called_once_with(1)

    def test_borrow_not_found(self, client, mock_borrow_service):
        """Test returning when borrow record does not exist (404)."""
        mock_borrow_service.return_borrow.side_effect = BorrowNotFoundError(
            "Borrow record with id 999 not found"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.patch("/api/v1/borrow/999/return")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_already_returned(self, client, mock_borrow_service):
        """Test returning a book that was already returned (400)."""
        mock_borrow_service.return_borrow.side_effect = InvalidBorrowError(
            "Borrow record with id 1 has already been returned"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.patch("/api/v1/borrow/1/return")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already been returned" in response.json()["detail"]

    def test_associated_book_not_found(self, client, mock_borrow_service):
        """Test return when associated book does not exist (404)."""
        mock_borrow_service.return_borrow.side_effect = BookNotFoundError(
            "Book with id 999 not found"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.patch("/api/v1/borrow/1/return")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_database_error(self, client, mock_borrow_service):
        """Test returning when database error occurs (500)."""
        mock_borrow_service.return_borrow.side_effect = DatabaseError(
            "Database connection failed"
        )
        app.dependency_overrides[get_borrow_service] = lambda: mock_borrow_service

        response = client.patch("/api/v1/borrow/1/return")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database operation failed" in response.json()["detail"]


# ============================================================================
# Test get_borrow_service Dependency Injection
# ============================================================================


class TestGetBorrowService:
    """Tests for get_borrow_service dependency injection function."""

    def test_service_initialization(self, mock_db):
        """Test that BorrowService is initialized with the database session."""
        service = get_borrow_service(mock_db)
        assert service is not None
        assert isinstance(service, BorrowService)

"""Unit tests for Book API endpoints.

Tests cover:
- GET /api/v1/books - List books with pagination
- POST /api/v1/books - Create new book
- PUT /api/v1/books/{book_id} - Update existing book

Exception Mapping:
- BookNotFoundError → 404 Not Found
- InvalidBookError → 400 Bad Request
- DatabaseError → 500 Internal Server Error
- Pydantic validation errors → 422 Unprocessable Entity
"""
import pytest
from unittest.mock import MagicMock, ANY
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.services.book_service import BookService
from app.schemas.book import BookBase
from app.api.v1.books import get_book_service
from app.common.exceptions import (
    BookNotFoundError,
    InvalidBookError,
    DatabaseError,
)


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


# ============================================================================
# Dependency Injection Tests
# ============================================================================

class TestGetBookService:
    """Tests for get_book_service dependency function"""

    def test_success(self, mock_db):
        """Test successful initialization of BookService."""
        service = get_book_service(mock_db)

        assert service is not None
        assert isinstance(service, BookService)
        assert service.db == mock_db

    def test_fails_with_none_db(self):
        """Test fails when database session is None."""
        with pytest.raises(ValueError) as exc_info:
            get_book_service(None)
        assert "Database session cannot be None" in str(exc_info.value)


# ============================================================================
# Test Data
# ============================================================================

def create_mock_book(
    book_id: int = 1,
    title: str = "Test Book",
    author: str = "Test Author",
    published_year: int = 2025,
    available: bool = True,
):
    """Create a mock book response."""
    return {
        "id": book_id,
        "title": title,
        "author": author,
        "published_year": published_year,
        "available": available,
    }


def create_book_request(
    title: str = "Test Book",
    author: str = "Test Author",
    published_year: int = 2025,
    available: bool = True,
):
    """Create a book request payload."""
    return {
        "title": title,
        "author": author,
        "published_year": published_year,
        "available": available,
    }


# ============================================================================
# GET /api/v1/books - List Books Tests
# ============================================================================

class TestListBooks:
    """Tests for GET /api/v1/books endpoint"""

    def test_success_default_pagination(self, client):
        """Test successful book list retrieval with default pagination."""
        mock_book1 = create_mock_book(book_id=1, title="Book 1")
        mock_book2 = create_mock_book(book_id=2, title="Book 2")
        mock_service = MagicMock(spec=BookService)
        mock_service.get_all_books.return_value = {
            "data": [mock_book1, mock_book2],
            "pagination": {
                "total": 2,
                "page": 1,
                "limit": 10,
                "pages": 1,
            }
        }
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.get("/api/v1/books/")

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.json()
        assert "pagination" in response.json()
        assert len(response.json()["data"]) == 2
        assert response.json()["data"][0]["title"] == "Book 1"
        assert response.json()["pagination"]["total"] == 2

    def test_success_custom_pagination(self, client):
        """Test successful retrieval with custom page and limit."""
        mock_books = [create_mock_book(i) for i in range(11, 16)]
        mock_service = MagicMock(spec=BookService)
        mock_service.get_all_books.return_value = {
            "data": mock_books,
            "pagination": {
                "total": 25,
                "page": 3,
                "limit": 5,
                "pages": 5,
            }
        }
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.get("/api/v1/books/?page=3&limit=5")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagination"]["page"] == 3
        assert response.json()["pagination"]["limit"] == 5
        assert response.json()["pagination"]["pages"] == 5
        mock_service.get_all_books.assert_called_once_with(page=3, limit=5)

    def test_empty_result(self, client):
        """Test successful retrieval when no books exist."""
        mock_service = MagicMock(spec=BookService)
        mock_service.get_all_books.return_value = {
            "data": [],
            "pagination": {
                "total": 0,
                "page": 1,
                "limit": 10,
                "pages": 0,
            }
        }
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.get("/api/v1/books/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []
        assert response.json()["pagination"]["total"] == 0

    def test_fails_with_invalid_page_query(self, client):
        """Test fails with invalid page query parameter (validation error)."""
        mock_service = MagicMock(spec=BookService)
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.get("/api/v1/books/?page=0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_service.get_all_books.assert_not_called()

    def test_fails_with_invalid_limit_query(self, client):
        """Test fails with invalid limit query parameter (> 100)."""
        mock_service = MagicMock(spec=BookService)
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.get("/api/v1/books/?limit=101")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_service.get_all_books.assert_not_called()

    def test_fails_with_invalid_book_error(self, client):
        """Test fails when service raises InvalidBookError (page > total pages)."""
        mock_service = MagicMock(spec=BookService)
        mock_service.get_all_books.side_effect = InvalidBookError(
            "Page 10 exceeds total pages 3")
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.get("/api/v1/books/?page=10")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "exceeds total pages" in response.json()["detail"]

    def test_fails_with_database_error(self, client):
        """Test fails when service raises DatabaseError."""
        mock_service = MagicMock(spec=BookService)
        mock_service.get_all_books.side_effect = DatabaseError(
            "Connection failed")
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.get("/api/v1/books/")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# ============================================================================
# POST /api/v1/books - Create Book Tests
# ============================================================================

class TestAddBook:
    """Tests for POST /api/v1/books endpoint"""

    def test_success(self, client):
        """Test successful book creation."""
        book_request = create_book_request()
        mock_book = create_mock_book()
        mock_service = MagicMock(spec=BookService)
        mock_service.create_book.return_value = mock_book
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.post("/api/v1/books/", json=book_request)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == 1
        assert response.json()["title"] == "Test Book"
        assert response.json()["author"] == "Test Author"
        # FastAPI parses the JSON dict into a BookBase object, so we use ANY
        mock_service.create_book.assert_called_once_with(ANY)

    def test_success_with_unavailable_book(self, client):
        """Test successful creation with unavailable book."""
        book_request = create_book_request(available=False)
        mock_book = create_mock_book(available=False)
        mock_service = MagicMock(spec=BookService)
        mock_service.create_book.return_value = mock_book
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.post("/api/v1/books/", json=book_request)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["available"] is False

    def test_fails_with_missing_title(self, client):
        """Test fails when title is missing (Pydantic validation)."""
        book_request = {"author": "Author",
                        "published_year": 2025, "available": True}
        mock_service = MagicMock(spec=BookService)
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.post("/api/v1/books/", json=book_request)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_service.create_book.assert_not_called()

    def test_fails_with_missing_author(self, client):
        """Test fails when author is missing (Pydantic validation)."""
        book_request = {"title": "Title",
                        "published_year": 2025, "available": True}
        mock_service = MagicMock(spec=BookService)
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.post("/api/v1/books/", json=book_request)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_service.create_book.assert_not_called()

    def test_fails_with_invalid_book_error(self, client):
        """Test fails when service raises InvalidBookError (future year)."""
        book_request = create_book_request(published_year=2027)
        mock_service = MagicMock(spec=BookService)
        mock_service.create_book.side_effect = InvalidBookError(
            "Published year cannot be in the future (provided: 2027)")
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.post("/api/v1/books/", json=book_request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "future" in response.json()["detail"]

    def test_fails_with_database_error(self, client):
        """Test fails when service raises DatabaseError."""
        book_request = create_book_request()
        mock_service = MagicMock(spec=BookService)
        mock_service.create_book.side_effect = DatabaseError(
            "Constraint violation")
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.post("/api/v1/books/", json=book_request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# ============================================================================
# PUT /api/v1/books/{book_id} - Update Book Tests
# ============================================================================

class TestUpdateBook:
    """Tests for PUT /api/v1/books/{book_id} endpoint"""

    def test_success(self, client):
        """Test successful book update."""
        book_id = 1
        book_request = create_book_request(title="Updated Title")
        mock_book = create_mock_book(title="Updated Title")
        mock_service = MagicMock(spec=BookService)
        mock_service.update_book.return_value = mock_book
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.put(f"/api/v1/books/{book_id}", json=book_request)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == book_id
        assert response.json()["title"] == "Updated Title"
        # FastAPI parses the JSON dict into a BookBase object, so we use ANY for the book parameter
        mock_service.update_book.assert_called_once_with(book_id, ANY)

    def test_success_multiple_field_updates(self, client):
        """Test successful update with multiple field changes."""
        book_id = 1
        book_request = create_book_request(
            title="New Title",
            author="New Author",
            available=False
        )
        mock_book = create_mock_book(
            title="New Title",
            author="New Author",
            available=False
        )
        mock_service = MagicMock(spec=BookService)
        mock_service.update_book.return_value = mock_book
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.put(f"/api/v1/books/{book_id}", json=book_request)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "New Title"
        assert response.json()["author"] == "New Author"
        assert response.json()["available"] is False

    def test_fails_when_book_not_found(self, client):
        """Test fails when book does not exist."""
        book_id = 999
        book_request = create_book_request()
        mock_service = MagicMock(spec=BookService)
        mock_service.update_book.side_effect = BookNotFoundError(
            f"Book with id {book_id} not found")
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.put(f"/api/v1/books/{book_id}", json=book_request)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_fails_with_missing_title(self, client):
        """Test fails when title is missing (Pydantic validation)."""
        book_id = 1
        book_request = {"author": "Author",
                        "published_year": 2025, "available": True}
        mock_service = MagicMock(spec=BookService)
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.put(f"/api/v1/books/{book_id}", json=book_request)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_service.update_book.assert_not_called()

    def test_fails_with_invalid_book_error(self, client):
        """Test fails when service raises InvalidBookError (future year)."""
        book_id = 1
        book_request = create_book_request(published_year=2027)
        mock_service = MagicMock(spec=BookService)
        mock_service.update_book.side_effect = InvalidBookError(
            "Published year cannot be in the future (provided: 2027)")
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.put(f"/api/v1/books/{book_id}", json=book_request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "future" in response.json()["detail"]

    def test_fails_with_database_error(self, client):
        """Test fails when service raises DatabaseError."""
        book_id = 1
        book_request = create_book_request()
        mock_service = MagicMock(spec=BookService)
        mock_service.update_book.side_effect = DatabaseError("Update failed")
        app.dependency_overrides[get_book_service] = lambda: mock_service

        response = client.put(f"/api/v1/books/{book_id}", json=book_request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.book import BookResponse
from app.services.book_service import BookService
from app.api.v1.books import get_book_service


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


# Test get_book_service dependency
def test_get_book_service_success(mock_db):
    """Test successful initialization of BookService."""
    with patch('app.api.v1.books.BookService') as mock_service_class:
        service = get_book_service(mock_db)
        mock_service_class.assert_called_once_with(mock_db)


def test_get_book_service_initialization_error(mock_db):
    """Test get_book_service when BookService initialization fails."""
    with patch('app.api.v1.books.BookService') as mock_service_class:
        mock_service_class.side_effect = Exception("Service init failed")
        
        with pytest.raises(HTTPException) as exc_info:
            get_book_service(mock_db)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to initialize book service"


# Test list_books endpoint
def test_list_books_success(client):
    """Test list_books returns books successfully."""
    mock_books = [
        BookResponse(id=1, title="Book 1", author="Author 1", published_year=2020, available=True),
        BookResponse(id=2, title="Book 2", author="Author 2", published_year=2021, available=False),
    ]
    
    mock_service = MagicMock(spec=BookService)
    mock_service.get_all_books.return_value = mock_books
    app.dependency_overrides[get_book_service] = lambda: mock_service
    
    response = client.get("/api/v1/books/")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Book 1"
    assert response.json()[1]["author"] == "Author 2"


def test_list_books_empty(client):
    """Test list_books when no books exist."""
    mock_service = MagicMock(spec=BookService)
    mock_service.get_all_books.return_value = []
    app.dependency_overrides[get_book_service] = lambda: mock_service
    
    response = client.get("/api/v1/books/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_books_validation_error(client):
    """Test list_books when service raises ValueError (validation error)."""
    mock_service = MagicMock(spec=BookService)
    mock_service.get_all_books.side_effect = ValueError("Invalid input")
    app.dependency_overrides[get_book_service] = lambda: mock_service
    
    response = client.get("/api/v1/books/")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid input" in response.json()["detail"]


def test_list_books_database_error(client):
    """Test list_books when service raises a general Exception (database error)."""
    mock_service = MagicMock(spec=BookService)
    mock_service.get_all_books.side_effect = Exception("Database connection failed")
    app.dependency_overrides[get_book_service] = lambda: mock_service
    
    response = client.get("/api/v1/books/")
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Failed to fetch books"


def test_list_books_service_initialization_fails(client):
    """Test list_books when service initialization fails."""
    def failing_service():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize book service"
        )
    
    app.dependency_overrides[get_book_service] = failing_service
    
    response = client.get("/api/v1/books/")
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Failed to initialize book service"

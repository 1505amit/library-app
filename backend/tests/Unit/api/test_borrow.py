import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.schemas.borrow import BorrowResponse, BorrowRequest
from app.services.borrow_service import BorrowService
from app.api.v1.borrow import get_borrow_service


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
def mock_borrow_response():
    """Mock borrow response fixture."""
    return BorrowResponse(
        id=1,
        book_id=1,
        member_id=1,
        borrowed_at=datetime.utcnow(),
        returned_at=None
    )

# Test get_borrow_service dependency


def test_get_borrow_service_success(mock_db):
    """Test successful initialization of BorrowService."""
    with patch('app.api.v1.borrow.BorrowService') as mock_service_class:
        service = get_borrow_service(mock_db)
        mock_service_class.assert_called_once_with(mock_db)


def test_get_borrow_service_initialization_error(mock_db):
    """Test get_borrow_service when BorrowService initialization fails."""
    with patch('app.api.v1.borrow.BorrowService') as mock_service_class:
        mock_service_class.side_effect = Exception("Service init failed")

        with pytest.raises(HTTPException) as exc_info:
            get_borrow_service(mock_db)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to initialize borrow service"


# Test borrow_book endpoint
def test_borrow_book_success(client, mock_borrow_response):
    """Test successful book borrowing."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.borrow_book.return_value = mock_borrow_response
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    borrow_request = {"book_id": 1, "member_id": 1}
    response = client.post("/api/v1/borrow/", json=borrow_request)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["book_id"] == 1
    assert response.json()["member_id"] == 1
    assert response.json()["returned_at"] is None
    mock_service.borrow_book.assert_called_once()


def test_borrow_book_not_found(client):
    """Test borrowing when book does not exist."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.borrow_book.side_effect = ValueError(
        "Book with id 999 not found")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    borrow_request = {"book_id": 999, "member_id": 1}
    response = client.post("/api/v1/borrow/", json=borrow_request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not found" in response.json()["detail"]


def test_borrow_book_not_available(client):
    """Test borrowing when book is not available."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.borrow_book.side_effect = ValueError(
        "Book with id 1 is not available")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    borrow_request = {"book_id": 1, "member_id": 1}
    response = client.post("/api/v1/borrow/", json=borrow_request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not available" in response.json()["detail"]


def test_borrow_book_member_not_found(client):
    """Test borrowing when member does not exist."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.borrow_book.side_effect = ValueError(
        "Member with id 999 not found")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    borrow_request = {"book_id": 1, "member_id": 999}
    response = client.post("/api/v1/borrow/", json=borrow_request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not found" in response.json()["detail"]


def test_borrow_book_member_not_active(client):
    """Test borrowing when member is not active."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.borrow_book.side_effect = ValueError(
        "Member with id 1 is not active")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    borrow_request = {"book_id": 1, "member_id": 1}
    response = client.post("/api/v1/borrow/", json=borrow_request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not active" in response.json()["detail"]


def test_borrow_book_database_error(client):
    """Test borrowing when database error occurs."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.borrow_book.side_effect = Exception(
        "Database connection failed")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    borrow_request = {"book_id": 1, "member_id": 1}
    response = client.post("/api/v1/borrow/", json=borrow_request)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to borrow book" in response.json()["detail"]

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.schemas.borrow import BorrowResponse, BorrowRequest, BorrowDetailedResponse
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


@pytest.fixture
def mock_borrow_detailed_response():
    """Mock detailed borrow response fixture."""
    return BorrowDetailedResponse(
        id=1,
        book_id=1,
        member_id=1,
        borrowed_at=datetime.utcnow(),
        returned_at=None,
        book={
            "id": 1,
            "title": "Test Book",
            "author": "Test Author",
            "published_year": 2025
        },
        member={
            "id": 1,
            "name": "Test Member",
            "email": "test@example.com"
        }
    )


@pytest.fixture
def mock_returned_borrow_response():
    """Mock returned borrow response fixture."""
    return BorrowDetailedResponse(
        id=2,
        book_id=2,
        member_id=2,
        borrowed_at=datetime(2026, 1, 1),
        returned_at=datetime(2026, 2, 1),
        book={
            "id": 2,
            "title": "Returned Book",
            "author": "Author Name",
            "published_year": 2021
        },
        member={
            "id": 2,
            "name": "Another Member",
            "email": "another@example.com"
        }
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


# Test get_all_borrows endpoint
def test_get_all_borrows_default_include_returned(client, mock_borrow_detailed_response, mock_returned_borrow_response):
    """Test getting all borrows with include_returned=True (default)."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.get_all_borrows.return_value = [
        mock_borrow_detailed_response,
        mock_returned_borrow_response
    ]
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.get("/api/v1/borrow/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[0]["returned_at"] is None
    assert data[1]["id"] == 2
    assert data[1]["returned_at"] is not None
    mock_service.get_all_borrows.assert_called_once_with(include_returned=True)


def test_get_all_borrows_with_include_returned_true(client, mock_borrow_detailed_response, mock_returned_borrow_response):
    """Test getting all borrows with include_returned=True explicitly."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.get_all_borrows.return_value = [
        mock_borrow_detailed_response,
        mock_returned_borrow_response
    ]
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.get("/api/v1/borrow/?include_returned=true")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    mock_service.get_all_borrows.assert_called_once_with(include_returned=True)


def test_get_all_borrows_with_include_returned_false(client, mock_borrow_detailed_response):
    """Test getting only active borrows with include_returned=False."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.get_all_borrows.return_value = [
        mock_borrow_detailed_response
    ]
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.get("/api/v1/borrow/?include_returned=false")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["returned_at"] is None
    mock_service.get_all_borrows.assert_called_once_with(
        include_returned=False)


def test_get_all_borrows_empty_list(client):
    """Test getting borrows when no records exist."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.get_all_borrows.return_value = []
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.get("/api/v1/borrow/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0
    mock_service.get_all_borrows.assert_called_once_with(include_returned=True)


def test_get_all_borrows_validation_error(client):
    """Test get_all_borrows when service raises ValueError."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.get_all_borrows.side_effect = ValueError(
        "Failed to retrieve borrow records")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.get("/api/v1/borrow/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Failed to retrieve borrow records" in response.json()["detail"]


def test_get_all_borrows_database_error(client):
    """Test get_all_borrows when service raises generic Exception."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.get_all_borrows.side_effect = Exception(
        "Database connection failed")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.get("/api/v1/borrow/")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to retrieve borrow records" in response.json()["detail"]


# Test return_book endpoint
def test_return_book_success(client, mock_returned_borrow_response):
    """Test successful book return."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.return_borrow.return_value = mock_returned_borrow_response
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.patch("/api/v1/borrow/1/return")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 2
    assert data["book_id"] == 2
    assert data["member_id"] == 2
    assert data["returned_at"] is not None
    mock_service.return_borrow.assert_called_once_with(1)


def test_return_book_not_found(client):
    """Test returning when borrow record does not exist."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.return_borrow.side_effect = ValueError(
        "Borrow record with id 999 not found")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.patch("/api/v1/borrow/999/return")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not found" in response.json()["detail"]


def test_return_book_already_returned(client):
    """Test returning a book that was already returned."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.return_borrow.side_effect = ValueError(
        "Borrow record with id 1 has already been returned")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.patch("/api/v1/borrow/1/return")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already been returned" in response.json()["detail"]


def test_return_book_book_not_found(client):
    """Test return when associated book does not exist (edge case)."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.return_borrow.side_effect = ValueError(
        "Book with id 999 not found")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.patch("/api/v1/borrow/1/return")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not found" in response.json()["detail"]


def test_return_book_database_error(client):
    """Test returning when database error occurs."""
    mock_service = MagicMock(spec=BorrowService)
    mock_service.return_borrow.side_effect = Exception(
        "Database connection failed")
    app.dependency_overrides[get_borrow_service] = lambda: mock_service

    response = client.patch("/api/v1/borrow/1/return")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to return book" in response.json()["detail"]

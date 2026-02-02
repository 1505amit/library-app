import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.member import MemberResponse, MemberBase
from app.services.member_service import MemberService
from app.api.v1.members import get_member_service


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    return MagicMock()


@pytest.fixture
def member_base():
    """Sample MemberBase object for testing."""
    return MemberBase(name="John Doe", email="john@example.com", phone="1234567890")


@pytest.fixture
def member_response():
    """Sample MemberResponse object for testing."""
    return MemberResponse(id=1, name="John Doe", email="john@example.com", phone="1234567890", active=True)


@pytest.fixture(autouse=True)
def clear_overrides():
    """Clear dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()


# Test get_member_service dependency
def test_get_member_service_success(mock_db):
    """Test successful initialization of MemberService."""
    with patch('app.api.v1.members.MemberService') as mock_service_class:
        service = get_member_service(mock_db)
        mock_service_class.assert_called_once_with(mock_db)


def test_get_member_service_initialization_error(mock_db):
    """Test get_member_service when MemberService initialization fails."""
    with patch('app.api.v1.members.MemberService') as mock_service_class:
        mock_service_class.side_effect = Exception("Service init failed")

        with pytest.raises(HTTPException) as exc_info:
            get_member_service(mock_db)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to initialize member service"


# Test add_member endpoint
def test_add_member_success(client, member_base, member_response):
    """Test add_member creates a member successfully."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.create_member.return_value = member_response
    app.dependency_overrides[get_member_service] = lambda: mock_service

    response = client.post("/api/v1/members/", json=member_base.model_dump())

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["phone"] == "1234567890"
    assert data["active"] is True


def test_add_member_without_optional_phone(client, member_response):
    """Test add_member without optional phone field."""
    member_no_phone = MemberBase(name="Jane Doe", email="jane@example.com")
    mock_service = MagicMock(spec=MemberService)
    mock_service.create_member.return_value = MemberResponse(
        id=2, name="Jane Doe", email="jane@example.com", phone=None, active=True
    )
    app.dependency_overrides[get_member_service] = lambda: mock_service

    response = client.post(
        "/api/v1/members/", json=member_no_phone.model_dump())

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"
    assert data["phone"] is None


def test_add_member_duplicate_email(client, member_base):
    """Test add_member fails with duplicate email (validation error)."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.create_member.side_effect = ValueError(
        "Email john@example.com already exists")
    app.dependency_overrides[get_member_service] = lambda: mock_service

    response = client.post("/api/v1/members/", json=member_base.model_dump())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_add_member_validation_error(client, member_base):
    """Test add_member when service raises ValueError for validation."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.create_member.side_effect = ValueError("Invalid email format")
    app.dependency_overrides[get_member_service] = lambda: mock_service

    response = client.post("/api/v1/members/", json=member_base.model_dump())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid email format" in response.json()["detail"]


def test_add_member_database_error(client, member_base):
    """Test add_member when service raises a general Exception (database error)."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.create_member.side_effect = Exception(
        "Database connection failed")
    app.dependency_overrides[get_member_service] = lambda: mock_service

    response = client.post("/api/v1/members/", json=member_base.model_dump())

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to create member" in response.json()["detail"]


def test_add_member_missing_name(client):
    """Test add_member fails when required name field is missing."""
    invalid_member = {"email": "john@example.com", "phone": "1234567890"}

    response = client.post("/api/v1/members/", json=invalid_member)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_add_member_missing_email(client):
    """Test add_member fails when required email field is missing."""
    invalid_member = {"name": "John Doe", "phone": "1234567890"}

    response = client.post("/api/v1/members/", json=invalid_member)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_add_member_empty_name(client):
    """Test add_member fails with empty name."""
    invalid_member = {"name": "", "email": "john@example.com"}

    response = client.post("/api/v1/members/", json=invalid_member)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_add_member_empty_email(client):
    """Test add_member fails with empty email."""
    invalid_member = {"name": "John Doe", "email": ""}

    response = client.post("/api/v1/members/", json=invalid_member)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

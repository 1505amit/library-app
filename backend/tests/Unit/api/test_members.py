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


# Test update_member endpoint


def test_update_member_success(client, member_base, member_response):
    """Test update_member updates a member successfully."""
    updated_member = MemberResponse(
        id=1, name="Jane Smith", email="jane@example.com", phone="9876543210", active=True
    )
    mock_service = MagicMock(spec=MemberService)
    mock_service.update_member.return_value = updated_member
    app.dependency_overrides[get_member_service] = lambda: mock_service

    update_data = MemberBase(
        name="Jane Smith", email="jane@example.com", phone="9876543210")
    response = client.put("/api/v1/members/1", json=update_data.model_dump())

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Jane Smith"
    assert data["email"] == "jane@example.com"
    assert data["phone"] == "9876543210"
    mock_service.update_member.assert_called_once_with(1, update_data)


def test_update_member_not_found(client):
    """Test update_member fails when member not found."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.update_member.side_effect = ValueError(
        "Member with id 999 not found")
    app.dependency_overrides[get_member_service] = lambda: mock_service

    update_data = {"name": "Updated Name", "email": "updated@example.com"}
    response = client.put("/api/v1/members/999", json=update_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_update_member_duplicate_email(client):
    """Test update_member fails with duplicate email."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.update_member.side_effect = ValueError(
        "Email john@example.com already exists")
    app.dependency_overrides[get_member_service] = lambda: mock_service

    update_data = {"name": "John Doe",
                   "email": "john@example.com", "phone": "1234567890"}
    response = client.put("/api/v1/members/1", json=update_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_update_member_database_error(client):
    """Test update_member when database error occurs."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.update_member.side_effect = Exception(
        "Database connection failed")
    app.dependency_overrides[get_member_service] = lambda: mock_service

    update_data = {"name": "John Doe", "email": "john@example.com"}
    response = client.put("/api/v1/members/1", json=update_data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to update member" in response.json()["detail"]


def test_update_member_missing_name(client):
    """Test update_member fails when required name field is missing."""
    invalid_update = {"email": "john@example.com", "phone": "1234567890"}

    response = client.put("/api/v1/members/1", json=invalid_update)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_member_missing_email(client):
    """Test update_member fails when required email field is missing."""
    invalid_update = {"name": "John Doe", "phone": "1234567890"}

    response = client.put("/api/v1/members/1", json=invalid_update)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Test list_members endpoint


def test_list_members_success(client, member_response):
    """Test list_members returns all members successfully."""
    mock_members = [
        MemberResponse(id=1, name="John Doe", email="john@example.com",
                       phone="1234567890", active=True),
        MemberResponse(id=2, name="Jane Smith",
                       email="jane@example.com", phone="9876543210", active=True),
        MemberResponse(id=3, name="Bob Johnson",
                       email="bob@example.com", phone=None, active=False),
    ]

    mock_service = MagicMock(spec=MemberService)
    mock_service.get_all_members.return_value = mock_members
    app.dependency_overrides[get_member_service] = lambda: mock_service

    response = client.get("/api/v1/members/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "John Doe"
    assert data[1]["email"] == "jane@example.com"
    assert data[2]["active"] is False


def test_list_members_empty(client):
    """Test list_members when no members exist."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.get_all_members.return_value = []
    app.dependency_overrides[get_member_service] = lambda: mock_service

    response = client.get("/api/v1/members/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_members_validation_error(client):
    """Test list_members when service raises ValueError (validation error)."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.get_all_members.side_effect = ValueError(
        "Invalid query parameters")
    app.dependency_overrides[get_member_service] = lambda: mock_service

    response = client.get("/api/v1/members/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid query parameters" in response.json()["detail"]


def test_list_members_database_error(client):
    """Test list_members when service raises a general Exception (database error)."""
    mock_service = MagicMock(spec=MemberService)
    mock_service.get_all_members.side_effect = Exception(
        "Database connection failed")
    app.dependency_overrides[get_member_service] = lambda: mock_service

    response = client.get("/api/v1/members/")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to retrieve members" in response.json()["detail"]

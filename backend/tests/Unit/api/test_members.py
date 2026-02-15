"""Unit tests for Members API endpoints.

Tests cover:
- list_members() - GET /api/v1/members/ with pagination
- add_member() - POST /api/v1/members/ for creating members
- update_member() - PUT /api/v1/members/{id} for updating members

Exception Mapping (from app.common.exceptions):
- MemberNotFoundError: Member does not exist → 404
- InvalidMemberError: Business rule violation → 400
- DatabaseError: Database operation failed → 500
"""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.member import MemberResponse, MemberBase
from app.services.member_service import MemberService
from app.common.exceptions import (
    MemberNotFoundError,
    InvalidMemberError,
    DatabaseError,
)
from app.api.v1.members import get_member_service


# ============================================================================
# Test Data Constants
# ============================================================================

MEMBER_ID = 1
MEMBER_NAME = "John Doe"
MEMBER_EMAIL = "john@example.com"
MEMBER_PHONE = "1234567890"
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
def mock_member_service():
    """Mock MemberService fixture."""
    return MagicMock(spec=MemberService)


@pytest.fixture(autouse=True)
def clear_overrides():
    """Clear dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()


# ============================================================================
# Test Data Builders
# ============================================================================

def create_member_response(
    member_id: int = MEMBER_ID,
    name: str = MEMBER_NAME,
    email: str = MEMBER_EMAIL,
    phone: str = MEMBER_PHONE,
    active: bool = True,
) -> MemberResponse:
    """Create a member response object."""
    return MemberResponse(
        id=member_id,
        name=name,
        email=email,
        phone=phone,
        active=active,
    )


def create_paginated_member_response(
    members: list = None,
    total: int = 1,
    page: int = DEFAULT_PAGE,
    limit: int = DEFAULT_LIMIT,
) -> dict:
    """Create a paginated member response."""
    if members is None:
        members = [create_member_response()]

    total_pages = (total + limit - 1) // limit if total > 0 else 0
    return {
        "data": members,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": total_pages,
        }
    }


# ============================================================================
# list_members() Tests
# ============================================================================

class TestListMembers:
    """Tests for list_members endpoint"""

    def test_success_default_parameters(self, client, mock_member_service):
        """Test successful retrieval with default pagination."""
        members = [create_member_response()]
        paginated_response = create_paginated_member_response(
            members=members, total=1)
        mock_member_service.get_all_members.return_value = paginated_response
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        response = client.get("/api/v1/members/")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == MEMBER_ID
        assert data["pagination"]["total"] == 1
        assert data["pagination"]["page"] == DEFAULT_PAGE

    def test_success_multiple_members(self, client, mock_member_service):
        """Test retrieval returns multiple members."""
        members = [
            create_member_response(member_id=1, name="John Doe"),
            create_member_response(
                member_id=2, name="Jane Smith", email="jane@example.com"),
            create_member_response(
                member_id=3, name="Bob Johnson", email="bob@example.com"),
        ]
        paginated_response = create_paginated_member_response(
            members=members, total=3)
        mock_member_service.get_all_members.return_value = paginated_response
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        response = client.get("/api/v1/members/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][1]["name"] == "Jane Smith"

    def test_success_empty_result(self, client, mock_member_service):
        """Test retrieval returns empty list with correct pagination."""
        paginated_response = create_paginated_member_response(
            members=[], total=0)
        mock_member_service.get_all_members.return_value = paginated_response
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        response = client.get("/api/v1/members/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 0
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["pages"] == 0

    def test_pagination_second_page(self, client, mock_member_service):
        """Test pagination with custom page and limit."""
        members = [create_member_response(member_id=11)]
        paginated_response = create_paginated_member_response(
            members=members, total=25, page=2, limit=10
        )
        mock_member_service.get_all_members.return_value = paginated_response
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        response = client.get("/api/v1/members/?page=2&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["total"] == 25
        assert data["pagination"]["pages"] == 3
        mock_member_service.get_all_members.assert_called_once_with(
            page=2, limit=10)

    def test_fails_with_invalid_page_number(self, client, mock_member_service):
        """Test fails when page exceeds total pages."""
        mock_member_service.get_all_members.side_effect = InvalidMemberError(
            "Page 5 exceeds total pages 2"
        )
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        response = client.get("/api/v1/members/?page=5&limit=10")

        assert response.status_code == 400
        assert "exceeds total pages" in response.json()["detail"]

    def test_raises_database_error(self, client, mock_member_service):
        """Test raises DatabaseError when query fails."""
        mock_member_service.get_all_members.side_effect = DatabaseError(
            "Failed to query members"
        )
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        response = client.get("/api/v1/members/")

        assert response.status_code == 500


# ============================================================================
# add_member() Tests
# ============================================================================

class TestAddMember:
    """Tests for add_member endpoint"""

    def test_success(self, client, mock_member_service):
        """Test successful member creation."""
        created_member = create_member_response()
        mock_member_service.create_member.return_value = created_member
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        member_data = {
            "name": MEMBER_NAME,
            "email": MEMBER_EMAIL,
            "phone": MEMBER_PHONE,
        }
        response = client.post("/api/v1/members/", json=member_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == MEMBER_ID
        assert data["name"] == MEMBER_NAME
        assert data["email"] == MEMBER_EMAIL
        assert data["phone"] == MEMBER_PHONE
        assert data["active"] is True

    def test_success_without_phone(self, client, mock_member_service):
        """Test successful creation without optional phone field."""
        created_member = create_member_response(phone=None)
        mock_member_service.create_member.return_value = created_member
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        member_data = {
            "name": MEMBER_NAME,
            "email": MEMBER_EMAIL,
        }
        response = client.post("/api/v1/members/", json=member_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == MEMBER_ID
        assert data["name"] == MEMBER_NAME
        assert data["email"] == MEMBER_EMAIL
        assert data["phone"] is None
        assert data["active"] is True

    def test_fails_with_duplicate_email(self, client, mock_member_service):
        """Test fails when email already exists."""
        mock_member_service.create_member.side_effect = InvalidMemberError(
            f"Email {MEMBER_EMAIL} already exists"
        )
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        member_data = {
            "name": MEMBER_NAME,
            "email": MEMBER_EMAIL,
            "phone": MEMBER_PHONE,
        }
        response = client.post("/api/v1/members/", json=member_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_fails_with_invalid_email(self, client):
        """Test fails when email is invalid (Pydantic validation)."""
        member_data = {
            "name": MEMBER_NAME,
            "email": "invalid-email",
            "phone": MEMBER_PHONE,
        }
        response = client.post("/api/v1/members/", json=member_data)

        # Pydantic validates email format and returns 422
        assert response.status_code == 422

    def test_fails_with_empty_name(self, client):
        """Test fails when name is empty (Pydantic validation)."""
        member_data = {
            "name": "",
            "email": MEMBER_EMAIL,
            "phone": MEMBER_PHONE,
        }
        response = client.post("/api/v1/members/", json=member_data)

        # Pydantic validates min_length and returns 422
        assert response.status_code == 422

    def test_fails_with_missing_name(self, client):
        """Test fails when name field is missing."""
        member_data = {
            "email": MEMBER_EMAIL,
            "phone": MEMBER_PHONE,
        }
        response = client.post("/api/v1/members/", json=member_data)

        assert response.status_code == 422

    def test_fails_with_missing_email(self, client):
        """Test fails when email field is missing."""
        member_data = {
            "name": MEMBER_NAME,
            "phone": MEMBER_PHONE,
        }
        response = client.post("/api/v1/members/", json=member_data)

        assert response.status_code == 422

    def test_raises_database_error(self, client, mock_member_service):
        """Test raises DatabaseError on database operation failure."""
        mock_member_service.create_member.side_effect = DatabaseError(
            "Failed to create member"
        )
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        member_data = {
            "name": MEMBER_NAME,
            "email": MEMBER_EMAIL,
            "phone": MEMBER_PHONE,
        }
        response = client.post("/api/v1/members/", json=member_data)

        assert response.status_code == 500


# ============================================================================
# update_member() Tests
# ============================================================================

class TestUpdateMember:
    """Tests for update_member endpoint"""

    def test_success(self, client, mock_member_service):
        """Test successful member update."""
        updated_member = create_member_response(
            name="Jane Smith", email="jane@example.com")
        mock_member_service.update_member.return_value = updated_member
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        member_data = {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": MEMBER_PHONE,
        }
        response = client.put(f"/api/v1/members/{MEMBER_ID}", json=member_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == MEMBER_ID
        assert data["name"] == "Jane Smith"
        assert data["email"] == "jane@example.com"

    def test_success_update_phone_only(self, client, mock_member_service):
        """Test successful update of phone field only."""
        updated_member = create_member_response(phone="9876543210")
        mock_member_service.update_member.return_value = updated_member
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        member_data = {
            "name": MEMBER_NAME,
            "email": MEMBER_EMAIL,
            "phone": "9876543210",
        }
        response = client.put(f"/api/v1/members/{MEMBER_ID}", json=member_data)

        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "9876543210"

    def test_fails_when_member_not_found(self, client, mock_member_service):
        """Test fails when member does not exist."""
        mock_member_service.update_member.side_effect = MemberNotFoundError(
            "Member with id 999 not found"
        )
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        member_data = {
            "name": MEMBER_NAME,
            "email": MEMBER_EMAIL,
            "phone": MEMBER_PHONE,
        }
        response = client.put("/api/v1/members/999", json=member_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_fails_with_duplicate_email(self, client, mock_member_service):
        """Test fails when email already exists."""
        mock_member_service.update_member.side_effect = InvalidMemberError(
            "Email already exists"
        )
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        member_data = {
            "name": MEMBER_NAME,
            "email": "existing@example.com",
            "phone": MEMBER_PHONE,
        }
        response = client.put(f"/api/v1/members/{MEMBER_ID}", json=member_data)

        assert response.status_code == 400
        assert "exists" in response.json()["detail"]

    def test_fails_with_invalid_name(self, client):
        """Test fails when name is invalid (Pydantic validation)."""
        member_data = {
            "name": "",
            "email": MEMBER_EMAIL,
            "phone": MEMBER_PHONE,
        }
        response = client.put(f"/api/v1/members/{MEMBER_ID}", json=member_data)

        # Pydantic validates min_length and returns 422
        assert response.status_code == 422

    def test_fails_with_missing_name(self, client):
        """Test fails when name field is missing."""
        member_data = {
            "email": MEMBER_EMAIL,
            "phone": MEMBER_PHONE,
        }
        response = client.put(f"/api/v1/members/{MEMBER_ID}", json=member_data)

        assert response.status_code == 422

    def test_fails_with_missing_email(self, client):
        """Test fails when email field is missing."""
        member_data = {
            "name": MEMBER_NAME,
            "phone": MEMBER_PHONE,
        }
        response = client.put(f"/api/v1/members/{MEMBER_ID}", json=member_data)

        assert response.status_code == 422

    def test_raises_database_error(self, client, mock_member_service):
        """Test raises DatabaseError on database operation failure."""
        mock_member_service.update_member.side_effect = DatabaseError(
            "Failed to update member"
        )
        app.dependency_overrides[get_member_service] = lambda: mock_member_service

        member_data = {
            "name": MEMBER_NAME,
            "email": MEMBER_EMAIL,
            "phone": MEMBER_PHONE,
        }
        response = client.put(f"/api/v1/members/{MEMBER_ID}", json=member_data)

        assert response.status_code == 500

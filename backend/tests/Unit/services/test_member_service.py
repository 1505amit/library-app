"""Unit tests for MemberService business logic.

Tests cover:
- MemberService initialization
- get_all_members() with pagination and validation
- get_member_by_id() for retrieving single members
- create_member() with validation and exception handling
- update_member() with validation and exception handling

Exception Mapping (from app.common.exceptions):
- MemberNotFoundError: Member does not exist
- InvalidMemberError: Business rule violation (empty name/email, duplicate email)
- DatabaseError: Database operation failures
"""
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.member_service import MemberService
from app.schemas.member import MemberBase
from app.models.member import Member
from app.common.exceptions import (
    MemberNotFoundError,
    InvalidMemberError,
    DatabaseError,
)


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
def mock_db():
    """Mock database session fixture."""
    return MagicMock(spec=Session)


@pytest.fixture
def member_service(mock_db):
    """MemberService fixture with mocked repositories."""
    service = MemberService(mock_db)
    # Mock the repository
    service.member_repository = MagicMock()
    return service


# ============================================================================
# Test Data Builders
# ============================================================================

def create_mock_member(
    member_id: int = MEMBER_ID,
    name: str = MEMBER_NAME,
    email: str = MEMBER_EMAIL,
    phone: str = MEMBER_PHONE,
    active: bool = True,
):
    """Create a mock member object."""
    member = MagicMock(spec=Member)
    member.id = member_id
    member.name = name
    member.email = email
    member.phone = phone
    member.active = active
    return member


def create_member_request(
    name: str = MEMBER_NAME,
    email: str = MEMBER_EMAIL,
    phone: str = MEMBER_PHONE,
):
    """Create a member request object."""
    return MemberBase(name=name, email=email, phone=phone)


def create_paginated_member_response(
    members: list,
    page: int = DEFAULT_PAGE,
    limit: int = DEFAULT_LIMIT,
    total: int = None,
):
    """Create a paginated member response."""
    if total is None:
        total = len(members)
    pages = (total + limit - 1) // limit
    return {
        "data": members,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        }
    }


# ============================================================================
# MemberService Initialization Tests
# ============================================================================

class TestMemberServiceInitialization:
    """Tests for MemberService.__init__()"""

    def test_success(self, mock_db):
        """Test successful initialization with valid database session."""
        service = MemberService(mock_db)

        assert service.db == mock_db
        assert service.member_repository is not None

    def test_fails_with_none_db(self):
        """Test initialization fails when db is None."""
        with pytest.raises(ValueError) as exc_info:
            MemberService(None)
        assert "Database session cannot be None" in str(exc_info.value)


# ============================================================================
# get_member_by_id() Tests
# ============================================================================

class TestGetMemberById:
    """Tests for MemberService.get_member_by_id()"""

    def test_success(self, member_service):
        """Test successful retrieval of member by ID."""
        mock_member = create_mock_member()
        member_service.member_repository.get_member_by_id.return_value = mock_member

        result = member_service.get_member_by_id(MEMBER_ID)

        assert result.id == MEMBER_ID
        assert result.name == MEMBER_NAME
        assert result.email == MEMBER_EMAIL
        member_service.member_repository.get_member_by_id.assert_called_once_with(
            MEMBER_ID)

    def test_fails_when_member_not_found(self, member_service):
        """Test fails when member does not exist."""
        member_service.member_repository.get_member_by_id.return_value = None

        with pytest.raises(MemberNotFoundError) as exc_info:
            member_service.get_member_by_id(999)
        assert "Member with id 999 not found" in str(exc_info.value)

    def test_raises_database_error_on_query_failure(self, member_service):
        """Test raises DatabaseError when database query fails."""
        member_service.member_repository.get_member_by_id.side_effect = DatabaseError(
            "Query failed")

        with pytest.raises(DatabaseError) as exc_info:
            member_service.get_member_by_id(MEMBER_ID)
        assert "Query failed" in str(exc_info.value)


# ============================================================================
# create_member() Tests
# ============================================================================

class TestCreateMember:
    """Tests for MemberService.create_member()"""

    def test_success(self, member_service):
        """Test successful member creation."""
        member_request = create_member_request()
        mock_member = create_mock_member()
        member_service.member_repository.create_member.return_value = mock_member

        result = member_service.create_member(member_request)

        assert result.id == MEMBER_ID
        assert result.name == MEMBER_NAME
        member_service.member_repository.create_member.assert_called_once_with(
            member_request)

    def test_success_without_phone(self, member_service):
        """Test successful creation without optional phone."""
        member_request = MemberBase(name=MEMBER_NAME, email=MEMBER_EMAIL)
        mock_member = create_mock_member(phone=None)
        member_service.member_repository.create_member.return_value = mock_member

        result = member_service.create_member(member_request)

        assert result.id == MEMBER_ID
        assert result.phone is None
        member_service.member_repository.create_member.assert_called_once_with(
            member_request)

    def test_fails_with_duplicate_email(self, member_service):
        """Test fails when email already exists."""
        member_request = create_member_request()
        member_service.member_repository.create_member.side_effect = InvalidMemberError(
            "Email john@example.com already exists")

        with pytest.raises(InvalidMemberError) as exc_info:
            member_service.create_member(member_request)
        assert "already exists" in str(exc_info.value)

    def test_raises_database_error_on_creation_failure(self, member_service):
        """Test raises DatabaseError when database operation fails."""
        member_request = create_member_request()
        member_service.member_repository.create_member.side_effect = DatabaseError(
            "Failed to create member in database")

        with pytest.raises(DatabaseError) as exc_info:
            member_service.create_member(member_request)
        assert "Failed to create member" in str(exc_info.value)


# ============================================================================
# update_member() Tests
# ============================================================================

class TestUpdateMember:
    """Tests for MemberService.update_member()"""

    def test_success(self, member_service):
        """Test successful member update."""
        member_request = create_member_request()
        mock_member = create_mock_member()
        member_service.member_repository.get_member_by_id.return_value = mock_member
        member_service.member_repository.update_member.return_value = mock_member

        result = member_service.update_member(MEMBER_ID, member_request)

        assert result.id == MEMBER_ID
        member_service.member_repository.get_member_by_id.assert_called_once_with(
            MEMBER_ID)
        member_service.member_repository.update_member.assert_called_once_with(
            MEMBER_ID, member_request, mock_member)

    def test_success_updates_phone_only(self, member_service):
        """Test successful update changing only phone."""
        updated_request = MemberBase(
            name=MEMBER_NAME,
            email=MEMBER_EMAIL,
            phone="9999999999"
        )
        mock_member = create_mock_member()
        member_service.member_repository.get_member_by_id.return_value = mock_member
        member_service.member_repository.update_member.return_value = mock_member

        result = member_service.update_member(MEMBER_ID, updated_request)

        assert result.id == MEMBER_ID
        member_service.member_repository.update_member.assert_called_once_with(
            MEMBER_ID, updated_request, mock_member)

    def test_success_removes_phone(self, member_service):
        """Test successful update removing phone."""
        updated_request = MemberBase(
            name=MEMBER_NAME,
            email=MEMBER_EMAIL,
            phone=None
        )
        mock_member = create_mock_member(phone=None)
        member_service.member_repository.get_member_by_id.return_value = mock_member
        member_service.member_repository.update_member.return_value = mock_member

        result = member_service.update_member(MEMBER_ID, updated_request)

        assert result.phone is None

    def test_fails_when_member_not_found(self, member_service):
        """Test fails when member does not exist."""
        member_request = create_member_request()
        member_service.member_repository.get_member_by_id.return_value = None

        with pytest.raises(MemberNotFoundError) as exc_info:
            member_service.update_member(999, member_request)
        assert "Member with id 999 not found" in str(exc_info.value)

    def test_fails_with_duplicate_email(self, member_service):
        """Test fails when updating to existing email."""
        member_request = create_member_request(email="other@example.com")
        mock_member = create_mock_member()
        member_service.member_repository.get_member_by_id.return_value = mock_member
        member_service.member_repository.update_member.side_effect = InvalidMemberError(
            "Email other@example.com already exists")

        with pytest.raises(InvalidMemberError) as exc_info:
            member_service.update_member(MEMBER_ID, member_request)
        assert "already exists" in str(exc_info.value)

    def test_raises_database_error_on_update_failure(self, member_service):
        """Test raises DatabaseError when database operation fails."""
        member_request = create_member_request()
        mock_member = create_mock_member()
        member_service.member_repository.get_member_by_id.return_value = mock_member
        member_service.member_repository.update_member.side_effect = DatabaseError(
            "Failed to update member in database")

        with pytest.raises(DatabaseError) as exc_info:
            member_service.update_member(MEMBER_ID, member_request)
        assert "Failed to update member" in str(exc_info.value)
# ============================================================================
# get_all_members() Tests
# ============================================================================


class TestGetAllMembers:
    """Tests for MemberService.get_all_members()"""

    def test_success_default_parameters(self, member_service):
        """Test successful retrieval with default parameters."""
        mock_member = create_mock_member()
        member_service.member_repository.get_all_members.return_value = (
            [mock_member],
            1,
        )

        result = member_service.get_all_members()

        assert "data" in result
        assert "pagination" in result
        assert len(result["data"]) == 1
        assert result["data"][0].id == MEMBER_ID
        assert result["pagination"]["total"] == 1
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["limit"] == 10
        assert result["pagination"]["pages"] == 1
        member_service.member_repository.get_all_members.assert_called_once_with(
            offset=0, limit=10)

    def test_success_with_custom_page(self, member_service):
        """Test successful retrieval with custom page."""
        members = [create_mock_member(i) for i in range(2, 7)]
        member_service.member_repository.get_all_members.return_value = (
            members,
            25,
        )

        result = member_service.get_all_members(page=3, limit=5)

        assert len(result["data"]) == 5
        assert result["pagination"]["total"] == 25
        assert result["pagination"]["page"] == 3
        assert result["pagination"]["limit"] == 5
        assert result["pagination"]["pages"] == 5
        member_service.member_repository.get_all_members.assert_called_once_with(
            offset=10, limit=5)

    def test_success_has_proper_response_structure(self, member_service):
        """Test response has data and pagination keys."""
        mock_member = create_mock_member()
        member_service.member_repository.get_all_members.return_value = (
            [mock_member],
            1,
        )

        result = member_service.get_all_members()

        assert isinstance(result, dict)
        assert set(result.keys()) == {"data", "pagination"}
        assert isinstance(result["data"], list)
        assert isinstance(result["pagination"], dict)

    def test_empty_result(self, member_service):
        """Test retrieval when no members exist."""
        member_service.member_repository.get_all_members.return_value = ([], 0)

        result = member_service.get_all_members()

        assert result["data"] == []
        assert result["pagination"]["total"] == 0
        assert result["pagination"]["pages"] == 0

    def test_pagination_offset_calculation(self, member_service):
        """Test pagination offset is calculated correctly from page."""
        member_service.member_repository.get_all_members.return_value = ([], 0)

        # Page 1 should have offset 0
        member_service.get_all_members(page=1, limit=10)
        member_service.member_repository.get_all_members.assert_called_with(
            offset=0, limit=10)

        member_service.member_repository.reset_mock()
        member_service.member_repository.get_all_members.return_value = ([], 0)

        # Page 2 should have offset 10
        member_service.get_all_members(page=2, limit=10)
        member_service.member_repository.get_all_members.assert_called_with(
            offset=10, limit=10)

        member_service.member_repository.reset_mock()
        member_service.member_repository.get_all_members.return_value = ([], 0)

        # Page 5 should have offset 40
        member_service.get_all_members(page=5, limit=10)
        member_service.member_repository.get_all_members.assert_called_with(
            offset=40, limit=10)

    def test_fails_when_page_exceeds_total_pages(self, member_service):
        """Test fails when requested page exceeds total pages."""
        # Total 25 members, 10 per page = 3 pages total
        member_service.member_repository.get_all_members.return_value = ([
        ], 25)

        with pytest.raises(InvalidMemberError) as exc_info:
            member_service.get_all_members(page=5, limit=10)
        assert "exceeds total pages" in str(exc_info.value)

    def test_succeeds_on_exact_last_page(self, member_service):
        """Test succeeds when page equals total pages."""
        members = [create_mock_member(i) for i in range(21, 26)]
        member_service.member_repository.get_all_members.return_value = (
            members,
            25,
        )

        result = member_service.get_all_members(page=3, limit=10)

        assert len(result["data"]) == 5
        assert result["pagination"]["pages"] == 3

    def test_raises_database_error_on_query_failure(self, member_service):
        """Test raises DatabaseError when database query fails."""
        member_service.member_repository.get_all_members.side_effect = DatabaseError(
            "Query failed")

        with pytest.raises(DatabaseError) as exc_info:
            member_service.get_all_members()
        assert "Query failed" in str(exc_info.value)

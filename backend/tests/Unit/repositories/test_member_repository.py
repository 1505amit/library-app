"""Unit tests for MemberRepository data access layer.

Tests cover:
- MemberRepository initialization
- get_all_members() with pagination
- get_member_by_id() for retrieving single members
- create_member() for persistence
- update_member() for updating existing members

Note: Repository layer has NO business logic validation.
All validation is performed in the service layer.
"""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.repositories.member_repository import MemberRepository
from app.schemas.member import MemberBase
from app.models.member import Member
from app.common.exceptions import DatabaseError, InvalidMemberError


# ============================================================================
# Test Data Constants
# ============================================================================

MEMBER_ID = 1
MEMBER_NAME = "John Doe"
MEMBER_EMAIL = "john@example.com"
MEMBER_PHONE = "1234567890"
DEFAULT_OFFSET = 0
DEFAULT_LIMIT = 10


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    return MagicMock(spec=Session)


@pytest.fixture
def member_repository(mock_db):
    """MemberRepository fixture."""
    return MemberRepository(mock_db)


# ============================================================================
# Test Data Builders
# ============================================================================

def create_mock_member(
    member_id: int = MEMBER_ID,
    name: str = MEMBER_NAME,
    email: str = MEMBER_EMAIL,
    phone: str = MEMBER_PHONE,
    active: bool = True,
) -> Member:
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
) -> MemberBase:
    """Create a member request object."""
    return MemberBase(name=name, email=email, phone=phone)


# ============================================================================
# MemberRepository Initialization Tests
# ============================================================================

class TestMemberRepositoryInitialization:
    """Tests for MemberRepository.__init__()"""

    def test_success(self, mock_db):
        """Test successful initialization with valid database session."""
        repo = MemberRepository(mock_db)
        assert repo.db == mock_db

    def test_fails_with_none_db(self):
        """Test fails when database session is None."""
        with pytest.raises(ValueError) as exc_info:
            MemberRepository(None)
        assert "Database session cannot be None" in str(exc_info.value)


# ============================================================================
# get_member_by_id() Tests
# ============================================================================

class TestGetMemberById:
    """Tests for MemberRepository.get_member_by_id()"""

    def test_success(self, member_repository, mock_db):
        """Test successful retrieval of member by ID."""
        mock_member = create_mock_member()
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_member
        mock_db.query.return_value = mock_query

        result = member_repository.get_member_by_id(MEMBER_ID)

        assert result.id == MEMBER_ID
        assert result.name == MEMBER_NAME
        mock_db.query.assert_called_once_with(Member)

    def test_returns_none_when_not_found(self, member_repository, mock_db):
        """Test returns None when member does not exist."""
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        result = member_repository.get_member_by_id(999)

        assert result is None

    def test_raises_database_error_on_query_failure(self, member_repository, mock_db):
        """Test raises DatabaseError when database query fails."""
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = SQLAlchemyError(
            "Query failed")
        mock_db.query.return_value = mock_query

        with pytest.raises(DatabaseError) as exc_info:
            member_repository.get_member_by_id(MEMBER_ID)
        assert "Failed to retrieve member" in str(exc_info.value)


# ============================================================================
# create_member() Tests
# ============================================================================

class TestCreateMember:
    """Tests for MemberRepository.create_member()"""

    def test_success(self, member_repository, mock_db):
        """Test successful member creation."""
        member_request = create_member_request()
        mock_member = create_mock_member()

        # Setup mock to capture the Member constructor call
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Mock Member class to track calls
        with patch('app.repositories.member_repository.Member') as mock_member_class:
            mock_member_class.return_value = mock_member
            result = member_repository.create_member(member_request)

        assert result.id == MEMBER_ID
        assert result.name == MEMBER_NAME
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_member)

    def test_success_without_phone(self, member_repository, mock_db):
        """Test successful creation without optional phone."""
        member_request = MemberBase(name=MEMBER_NAME, email=MEMBER_EMAIL)
        mock_member = create_mock_member(phone=None)

        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        with patch('app.repositories.member_repository.Member') as mock_member_class:
            mock_member_class.return_value = mock_member
            result = member_repository.create_member(member_request)

        assert result.id == MEMBER_ID
        assert result.phone is None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_member)

    def test_raises_invalid_member_error_on_duplicate_email(self, member_repository, mock_db):
        """Test raises InvalidMemberError when email already exists during creation."""
        member_request = create_member_request()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock(
            side_effect=IntegrityError("Duplicate", "email", "constraint"))
        mock_db.rollback = MagicMock()

        with patch('app.repositories.member_repository.Member'):
            with pytest.raises(InvalidMemberError) as exc_info:
                member_repository.create_member(member_request)
            assert "already exists" in str(exc_info.value)
            mock_db.rollback.assert_called_once()

    def test_raises_database_error_on_other_integrity_error(self, member_repository, mock_db):
        """Test raises DatabaseError for other constraint violations."""
        member_request = create_member_request()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock(
            side_effect=IntegrityError("Other", "constraint", None))
        mock_db.rollback = MagicMock()

        with patch('app.repositories.member_repository.Member'):
            with pytest.raises(DatabaseError) as exc_info:
                member_repository.create_member(member_request)
            assert "constraint violation" in str(exc_info.value)
            mock_db.rollback.assert_called_once()

    def test_raises_database_error_on_sqlalchemy_error(self, member_repository, mock_db):
        """Test raises DatabaseError when SQLAlchemy error occurs."""
        member_request = create_member_request()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock(
            side_effect=SQLAlchemyError("Database error"))
        mock_db.rollback = MagicMock()

        with patch('app.repositories.member_repository.Member'):
            with pytest.raises(DatabaseError) as exc_info:
                member_repository.create_member(member_request)
            assert "Failed to create member" in str(exc_info.value)
            mock_db.rollback.assert_called_once()

    """Tests for MemberRepository.get_all_members()"""

    def test_success_default_parameters(self, member_repository, mock_db):
        """Test successful retrieval with default pagination."""
        mock_member = create_mock_member()
        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.offset.return_value.limit.return_value.all.return_value = [
            mock_member]
        mock_db.query.return_value = mock_query

        result, total = member_repository.get_all_members()

        assert len(result) == 1
        assert total == 1
        assert result[0].id == MEMBER_ID
        mock_query.offset.assert_called_once_with(0)
        mock_query.offset.return_value.limit.assert_called_once_with(10)

    def test_returns_tuple_with_total_count(self, member_repository, mock_db):
        """Test returns tuple of (members, total_count)."""
        members = [create_mock_member(i) for i in range(1, 6)]
        mock_query = MagicMock()
        mock_query.count.return_value = 25
        mock_query.offset.return_value.limit.return_value.all.return_value = members
        mock_db.query.return_value = mock_query

        records, total = member_repository.get_all_members(offset=0, limit=5)

        assert len(records) == 5
        assert total == 25

    def test_empty_result(self, member_repository, mock_db):
        """Test returns empty list when no members exist."""
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        result, total = member_repository.get_all_members()

        assert len(result) == 0
        assert total == 0

    def test_pagination_with_custom_offset(self, member_repository, mock_db):
        """Test pagination with custom offset and limit."""
        mock_member = create_mock_member()
        mock_query = MagicMock()
        mock_query.count.return_value = 50
        mock_query.offset.return_value.limit.return_value.all.return_value = [
            mock_member]
        mock_db.query.return_value = mock_query

        result, total = member_repository.get_all_members(offset=20, limit=10)

        mock_query.offset.assert_called_once_with(20)
        mock_query.offset.return_value.limit.assert_called_once_with(10)
        assert total == 50

    def test_pagination_large_offset(self, member_repository, mock_db):
        """Test pagination with large offset."""
        mock_query = MagicMock()
        mock_query.count.return_value = 500
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        result, total = member_repository.get_all_members(offset=400, limit=50)

        mock_query.offset.assert_called_once_with(400)
        mock_query.offset.return_value.limit.assert_called_once_with(50)
        assert total == 500

    def test_raises_database_error_on_query_failure(self, member_repository, mock_db):
        """Test raises DatabaseError when database query fails."""
        mock_query = MagicMock()
        mock_query.count.side_effect = SQLAlchemyError("Query failed")
        mock_db.query.return_value = mock_query

        with pytest.raises(DatabaseError) as exc_info:
            member_repository.get_all_members()
        assert "Failed to retrieve members" in str(exc_info.value)


# ============================================================================
# update_member() Tests
# ============================================================================

class TestUpdateMember:
    """Tests for MemberRepository.update_member()"""

    def test_success(self, member_repository, mock_db):
        """Test successful member update."""
        member_request = create_member_request()
        mock_member = create_mock_member()

        member_repository.update_member(MEMBER_ID, member_request, mock_member)

        # Verify attributes were set
        assert mock_member.name == MEMBER_NAME
        assert mock_member.email == MEMBER_EMAIL
        assert mock_member.phone == MEMBER_PHONE
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_member)

    def test_updates_specific_fields(self, member_repository, mock_db):
        """Test update sets correct fields on member object."""
        update_data = MemberBase(
            name="Jane Smith",
            email="jane@example.com",
            phone="9876543210",
        )
        mock_member = create_mock_member()

        member_repository.update_member(MEMBER_ID, update_data, mock_member)

        assert mock_member.name == "Jane Smith"
        assert mock_member.email == "jane@example.com"
        assert mock_member.phone == "9876543210"

    def test_updates_phone_without_phone(self, member_repository, mock_db):
        """Test update to remove phone field."""
        update_data = MemberBase(
            name=MEMBER_NAME,
            email=MEMBER_EMAIL,
            phone=None,
        )
        mock_member = create_mock_member()

        member_repository.update_member(MEMBER_ID, update_data, mock_member)

        assert mock_member.phone is None
        mock_db.commit.assert_called_once()

    def test_raises_invalid_member_error_on_duplicate_email(self, member_repository, mock_db):
        """Test raises InvalidMemberError when email already exists."""
        member_request = create_member_request()
        mock_member = create_mock_member()
        mock_db.commit.side_effect = IntegrityError(
            "Duplicate", "email", "constraint")
        mock_db.rollback = MagicMock()

        with pytest.raises(InvalidMemberError) as exc_info:
            member_repository.update_member(
                MEMBER_ID, member_request, mock_member)
        assert "already exists" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

    def test_raises_database_error_on_other_integrity_error(self, member_repository, mock_db):
        """Test raises DatabaseError for other constraint violations."""
        member_request = create_member_request()
        mock_member = create_mock_member()
        mock_db.commit.side_effect = IntegrityError(
            "Other", "constraint", None)
        mock_db.rollback = MagicMock()

        with pytest.raises(DatabaseError) as exc_info:
            member_repository.update_member(
                MEMBER_ID, member_request, mock_member)
        assert "constraint violation" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

    def test_raises_database_error_on_sqlalchemy_error(self, member_repository, mock_db):
        """Test raises DatabaseError when SQLAlchemy error occurs."""
        member_request = create_member_request()
        mock_member = create_mock_member()
        mock_db.commit.side_effect = SQLAlchemyError("Database error")
        mock_db.rollback = MagicMock()

        with pytest.raises(DatabaseError) as exc_info:
            member_repository.update_member(
                MEMBER_ID, member_request, mock_member)
        assert "Failed to update member" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

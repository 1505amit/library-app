import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.services.member_service import MemberService
from app.schemas.member import MemberBase, MemberResponse
from app.models.member import Member


@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    return MagicMock()


@pytest.fixture
def member_base():
    """Sample MemberBase object for testing."""
    return MemberBase(name="John Doe", email="john@example.com", phone="1234567890")


@pytest.fixture
def mock_repo_member():
    """Sample Member model object for testing (from repository)."""
    member = Member()
    member.id = 1
    member.name = "John Doe"
    member.email = "john@example.com"
    member.phone = "1234567890"
    member.active = True
    return member


# Test MemberService initialization
def test_member_service_initialization_success(mock_db):
    """Test successful initialization of MemberService."""
    service = MemberService(mock_db)

    assert service.db == mock_db
    assert service.member_repository is not None


def test_member_service_initialization_with_none_db():
    """Test MemberService initialization fails with None database."""
    with pytest.raises(ValueError) as exc_info:
        MemberService(None)

    assert "Database session cannot be None" in str(exc_info.value)


# Test create_member method
def test_create_member_success(mock_db, member_base, mock_repo_member):
    """Test successful member creation."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.create_member.return_value = mock_repo_member

        service = MemberService(mock_db)
        result = service.create_member(member_base)

        mock_repo.create_member.assert_called_once_with(member_base)
        assert result.id == 1
        assert result.name == "John Doe"
        assert result.email == "john@example.com"


def test_create_member_duplicate_email_error(mock_db, member_base):
    """Test create_member when duplicate email error occurs."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.create_member.side_effect = ValueError(
            "Email john@example.com already exists")

        service = MemberService(mock_db)

        with pytest.raises(ValueError) as exc_info:
            service.create_member(member_base)

        assert "already exists" in str(exc_info.value)


def test_create_member_database_integrity_error(mock_db, member_base):
    """Test create_member when database integrity error occurs."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.create_member.side_effect = ValueError(
            "Failed to create member in database")

        service = MemberService(mock_db)

        with pytest.raises(ValueError) as exc_info:
            service.create_member(member_base)

        assert "Failed to create member" in str(exc_info.value)


def test_create_member_sqlalchemy_error(mock_db, member_base):
    """Test create_member when SQLAlchemyError occurs."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.create_member.side_effect = SQLAlchemyError(
            "Connection lost")

        service = MemberService(mock_db)

        with pytest.raises(ValueError) as exc_info:
            service.create_member(member_base)

        assert "Failed to create member in database" in str(exc_info.value)


def test_create_member_unexpected_error(mock_db, member_base):
    """Test create_member when unexpected error occurs."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.create_member.side_effect = RuntimeError("Unexpected error")

        service = MemberService(mock_db)

        with pytest.raises(RuntimeError):
            service.create_member(member_base)

# Test update_member method


def test_update_member_success(mock_db, member_base, mock_repo_member):
    """Test successful member update."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        updated_member = mock_repo_member
        updated_member.name = "Jane Doe"
        mock_repo.update_member.return_value = updated_member

        service = MemberService(mock_db)
        result = service.update_member(1, member_base)

        mock_repo.update_member.assert_called_once_with(1, member_base)
        assert result.id == 1
        assert result.name == "Jane Doe"


def test_update_member_not_found(mock_db, member_base):
    """Test update_member when member not found."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.update_member.side_effect = ValueError(
            "Member with id 999 not found")

        service = MemberService(mock_db)

        with pytest.raises(ValueError) as exc_info:
            service.update_member(999, member_base)

        assert "not found" in str(exc_info.value)


def test_update_member_duplicate_email(mock_db, member_base):
    """Test update_member when duplicate email error occurs."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.update_member.side_effect = ValueError(
            "Email john@example.com already exists")

        service = MemberService(mock_db)

        with pytest.raises(ValueError) as exc_info:
            service.update_member(1, member_base)

        assert "already exists" in str(exc_info.value)


def test_update_member_sqlalchemy_error(mock_db, member_base):
    """Test update_member when SQLAlchemyError occurs."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.update_member.side_effect = SQLAlchemyError(
            "Connection lost")

        service = MemberService(mock_db)

        with pytest.raises(ValueError) as exc_info:
            service.update_member(1, member_base)

        assert "Failed to update member" in str(exc_info.value)


def test_update_member_unexpected_error(mock_db, member_base):
    """Test update_member when unexpected error occurs."""
    with patch('app.services.member_service.MemberRepository') as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.update_member.side_effect = RuntimeError("Unexpected error")

        service = MemberService(mock_db)

        with pytest.raises(RuntimeError):
            service.update_member(1, member_base)

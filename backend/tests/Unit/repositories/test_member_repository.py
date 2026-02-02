import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.repositories.member_repository import MemberRepository
from app.schemas.member import MemberBase
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
def member_no_phone():
    """Sample MemberBase object without phone for testing."""
    return MemberBase(name="Jane Doe", email="jane@example.com")


@pytest.fixture
def mock_db_member():
    """Sample Member model object from database."""
    member = Member(
        id=1,
        name="John Doe",
        email="john@example.com",
        phone="1234567890",
        active=True
    )
    return member


# Test MemberRepository initialization
def test_member_repository_initialization_success(mock_db):
    """Test successful initialization of MemberRepository."""
    repo = MemberRepository(mock_db)

    assert repo.db == mock_db


def test_member_repository_initialization_with_none_db():
    """Test MemberRepository initialization fails with None database."""
    with pytest.raises(ValueError) as exc_info:
        MemberRepository(None)

    assert "Database session cannot be None" in str(exc_info.value)


# Test create_member method
def test_create_member_success(mock_db, member_base, mock_db_member):
    """Test successful member creation in repository."""
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    # Mock the Member constructor to return our test member
    repo = MemberRepository(mock_db)

    # We need to mock the Member class creation
    with patch('app.repositories.member_repository.Member') as mock_member_class:
        mock_member_class.return_value = mock_db_member

        result = repo.create_member(member_base)

        # Verify database operations
        mock_db.add.assert_called_once_with(mock_db_member)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_db_member)

        # Verify result
        assert result.id == 1
        assert result.name == "John Doe"
        assert result.email == "john@example.com"
        assert result.phone == "1234567890"
        assert result.active is True


def test_create_member_without_phone(mock_db, member_no_phone):
    """Test member creation without optional phone field."""
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    mock_db_member_no_phone = Member(
        id=2,
        name="Jane Doe",
        email="jane@example.com",
        phone=None,
        active=True
    )

    repo = MemberRepository(mock_db)

    with patch('app.repositories.member_repository.Member') as mock_member_class:
        mock_member_class.return_value = mock_db_member_no_phone

        result = repo.create_member(member_no_phone)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        assert result.name == "Jane Doe"
        assert result.email == "jane@example.com"
        assert result.phone is None


def test_create_member_duplicate_email_error(mock_db, member_base):
    """Test create_member with duplicate email constraint violation."""
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock(side_effect=IntegrityError(
        "Duplicate", "email", "john@example.com"))
    mock_db.rollback = MagicMock()

    repo = MemberRepository(mock_db)

    with patch('app.repositories.member_repository.Member'):
        with pytest.raises(ValueError) as exc_info:
            repo.create_member(member_base)

        assert "already exists" in str(exc_info.value)
        mock_db.rollback.assert_called_once()


def test_create_member_other_integrity_error(mock_db, member_base):
    """Test create_member with other integrity constraint violation."""
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock(side_effect=IntegrityError(
        "Some other constraint", "violation", None))
    mock_db.rollback = MagicMock()

    repo = MemberRepository(mock_db)

    with patch('app.repositories.member_repository.Member'):
        with pytest.raises(ValueError) as exc_info:
            repo.create_member(member_base)

        assert "constraint violation" in str(exc_info.value)
        mock_db.rollback.assert_called_once()


def test_create_member_sqlalchemy_error(mock_db, member_base):
    """Test create_member when SQLAlchemyError occurs."""
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock(side_effect=SQLAlchemyError("Database error"))
    mock_db.rollback = MagicMock()

    repo = MemberRepository(mock_db)

    with patch('app.repositories.member_repository.Member'):
        with pytest.raises(SQLAlchemyError):
            repo.create_member(member_base)

        mock_db.rollback.assert_called_once()


def test_create_member_unexpected_error(mock_db, member_base):
    """Test create_member when unexpected error occurs."""
    mock_db.add = MagicMock(side_effect=RuntimeError("Unexpected error"))
    mock_db.rollback = MagicMock()

    repo = MemberRepository(mock_db)

    with patch('app.repositories.member_repository.Member'):
        with pytest.raises(RuntimeError):
            repo.create_member(member_base)

        mock_db.rollback.assert_called_once()


def test_create_member_member_dict_conversion(mock_db, member_base):
    """Test that member data is correctly converted to Member model."""
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    mock_db_member = Member()

    repo = MemberRepository(mock_db)

    with patch('app.repositories.member_repository.Member') as mock_member_class:
        mock_member_class.return_value = mock_db_member
        repo.create_member(member_base)

        # Verify Member was called with unpacked dict
        mock_member_class.assert_called_once_with(**member_base.dict())

# Test update_member method


def test_update_member_success(mock_db, member_base, mock_db_member):
    """Test successful member update in repository."""
    mock_db.query = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value.first.return_value = mock_db_member
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    repo = MemberRepository(mock_db)
    result = repo.update_member(1, member_base)

    # Verify query was made for the member
    mock_db.query.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_db_member)

    # Verify attributes were updated
    assert result.name == "John Doe"
    assert result.email == "john@example.com"


def test_update_member_not_found(mock_db, member_base):
    """Test update_member when member not found."""
    mock_db.query = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value.first.return_value = None
    mock_db.rollback = MagicMock()

    repo = MemberRepository(mock_db)

    with pytest.raises(ValueError) as exc_info:
        repo.update_member(999, member_base)

    assert "not found" in str(exc_info.value)
    mock_db.rollback.assert_not_called()


def test_update_member_duplicate_email_error(mock_db, member_base, mock_db_member):
    """Test update_member with duplicate email constraint violation."""
    mock_db.query = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value.first.return_value = mock_db_member

    # Mock the error
    mock_db.commit = MagicMock(side_effect=IntegrityError(
        "Duplicate", "email", "john@example.com"))
    mock_db.rollback = MagicMock()

    repo = MemberRepository(mock_db)

    with pytest.raises(ValueError) as exc_info:
        repo.update_member(1, member_base)

    assert "already exists" in str(exc_info.value)
    mock_db.rollback.assert_called_once()


def test_update_member_other_integrity_error(mock_db, member_base, mock_db_member):
    """Test update_member with other integrity constraint violation."""
    mock_db.query = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value.first.return_value = mock_db_member

    mock_db.commit = MagicMock(side_effect=IntegrityError(
        "Some other constraint", "violation", None))
    mock_db.rollback = MagicMock()

    repo = MemberRepository(mock_db)

    with pytest.raises(ValueError) as exc_info:
        repo.update_member(1, member_base)

    assert "constraint violation" in str(exc_info.value)
    mock_db.rollback.assert_called_once()


def test_update_member_sqlalchemy_error(mock_db, member_base, mock_db_member):
    """Test update_member when SQLAlchemyError occurs."""
    mock_db.query = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value.first.return_value = mock_db_member

    mock_db.commit = MagicMock(side_effect=SQLAlchemyError("Database error"))
    mock_db.rollback = MagicMock()

    repo = MemberRepository(mock_db)

    with pytest.raises(SQLAlchemyError):
        repo.update_member(1, member_base)

    mock_db.rollback.assert_called_once()


def test_update_member_unexpected_error(mock_db, member_base, mock_db_member):
    """Test update_member when unexpected error occurs."""
    mock_db.query = MagicMock(side_effect=RuntimeError("Unexpected error"))
    mock_db.rollback = MagicMock()

    repo = MemberRepository(mock_db)

    with pytest.raises(RuntimeError):
        repo.update_member(1, member_base)

    mock_db.rollback.assert_called_once()

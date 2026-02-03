import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.borrow_repository import BorrowRepository
from app.schemas.borrow import BorrowBase
from app.models.borrow import BorrowRecord
from app.models.book import Book
from app.models.member import Member


@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    return MagicMock()


@pytest.fixture
def borrow_repository(mock_db):
    """BorrowRepository fixture."""
    return BorrowRepository(mock_db)


@pytest.fixture
def borrow_base():
    """Sample BorrowBase fixture."""
    return BorrowBase(book_id=1, member_id=1)


@pytest.fixture
def mock_book():
    """Mock book fixture."""
    book = MagicMock(spec=Book)
    book.id = 1
    book.available = True
    return book


@pytest.fixture
def mock_member():
    """Mock member fixture."""
    member = MagicMock(spec=Member)
    member.id = 1
    member.active = True
    return member


@pytest.fixture
def mock_borrow_record():
    """Mock borrow record fixture."""
    borrow = MagicMock(spec=BorrowRecord)
    borrow.id = 1
    borrow.book_id = 1
    borrow.member_id = 1
    borrow.borrowed_at = datetime.utcnow()
    borrow.returned_at = None
    return borrow


# Test BorrowRepository initialization
def test_borrow_repository_initialization_success(mock_db):
    """Test successful BorrowRepository initialization."""
    repo = BorrowRepository(mock_db)
    assert repo.db == mock_db


def test_borrow_repository_initialization_with_none_db():
    """Test BorrowRepository initialization with None database."""
    with pytest.raises(ValueError) as exc_info:
        BorrowRepository(None)
    assert "Database session cannot be None" in str(exc_info.value)


# Test create_borrow
def test_create_borrow_success(borrow_repository, mock_db, borrow_base, mock_book, mock_member, mock_borrow_record):
    """Test successful borrow creation."""
    # Setup mocks
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_book, mock_member]
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    result = borrow_repository.create_borrow(borrow_base)

    # Verify book was marked as unavailable
    assert mock_book.available == False
    # Verify database operations
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_create_borrow_book_not_found(borrow_repository, mock_db, borrow_base):
    """Test create_borrow when book does not exist."""
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ValueError) as exc_info:
        borrow_repository.create_borrow(borrow_base)
    assert "not found" in str(exc_info.value)
    mock_db.rollback.assert_called_once()


def test_create_borrow_book_not_available(borrow_repository, mock_db, borrow_base, mock_book):
    """Test create_borrow when book is not available."""
    mock_book.available = False
    mock_db.query.return_value.filter.return_value.first.return_value = mock_book

    with pytest.raises(ValueError) as exc_info:
        borrow_repository.create_borrow(borrow_base)
    assert "not available" in str(exc_info.value)
    mock_db.rollback.assert_called_once()


def test_create_borrow_member_not_found(borrow_repository, mock_db, borrow_base, mock_book):
    """Test create_borrow when member does not exist."""
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_book, None]

    with pytest.raises(ValueError) as exc_info:
        borrow_repository.create_borrow(borrow_base)
    assert "not found" in str(exc_info.value)
    mock_db.rollback.assert_called_once()


def test_create_borrow_member_not_active(borrow_repository, mock_db, borrow_base, mock_book, mock_member):
    """Test create_borrow when member is not active."""
    mock_member.active = False
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_book, mock_member]

    with pytest.raises(ValueError) as exc_info:
        borrow_repository.create_borrow(borrow_base)
    assert "not active" in str(exc_info.value)
    mock_db.rollback.assert_called_once()


def test_create_borrow_database_error(borrow_repository, mock_db, borrow_base, mock_book, mock_member):
    """Test create_borrow when database error occurs."""
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_book, mock_member]
    mock_db.commit.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(SQLAlchemyError):
        borrow_repository.create_borrow(borrow_base)
    mock_db.rollback.assert_called_once()


def test_create_borrow_unexpected_error(borrow_repository, mock_db, borrow_base, mock_book, mock_member):
    """Test create_borrow when unexpected error occurs."""
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_book, mock_member]
    mock_db.commit.side_effect = Exception("Unexpected error")

    with pytest.raises(Exception):
        borrow_repository.create_borrow(borrow_base)
    mock_db.rollback.assert_called_once()

# Test get_all_borrows


def test_get_all_borrows_with_include_returned_true(borrow_repository, mock_db):
    """Test get_all_borrows returns all records when include_returned=True."""
    mock_active_borrow = MagicMock(spec=BorrowRecord)
    mock_active_borrow.id = 1
    mock_active_borrow.returned_at = None

    mock_returned_borrow = MagicMock(spec=BorrowRecord)
    mock_returned_borrow.id = 2
    mock_returned_borrow.returned_at = datetime.utcnow()

    mock_db.query.return_value.all.return_value = [
        mock_active_borrow,
        mock_returned_borrow
    ]

    result = borrow_repository.get_all_borrows(include_returned=True)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2
    mock_db.query.assert_called_once_with(BorrowRecord)
    # When include_returned=True, no filter is applied
    mock_db.query.return_value.filter.assert_not_called()
    mock_db.query.return_value.all.assert_called_once()


def test_get_all_borrows_with_include_returned_false(borrow_repository, mock_db):
    """Test get_all_borrows filters only active records when include_returned=False."""
    mock_active_borrow = MagicMock(spec=BorrowRecord)
    mock_active_borrow.id = 1
    mock_active_borrow.returned_at = None

    mock_db.query.return_value.filter.return_value.all.return_value = [
        mock_active_borrow
    ]

    result = borrow_repository.get_all_borrows(include_returned=False)

    assert len(result) == 1
    assert result[0].id == 1
    mock_db.query.assert_called_once_with(BorrowRecord)
    mock_db.query.return_value.filter.assert_called_once()
    mock_db.query.return_value.filter.return_value.all.assert_called_once()


def test_get_all_borrows_empty_list_include_returned_true(borrow_repository, mock_db):
    """Test get_all_borrows returns empty list when no records exist with include_returned=True."""
    mock_db.query.return_value.all.return_value = []

    result = borrow_repository.get_all_borrows(include_returned=True)

    assert len(result) == 0
    mock_db.query.return_value.all.assert_called_once()


def test_get_all_borrows_empty_list_include_returned_false(borrow_repository, mock_db):
    """Test get_all_borrows returns empty list when no active records exist with include_returned=False."""
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = borrow_repository.get_all_borrows(include_returned=False)

    assert len(result) == 0
    mock_db.query.return_value.filter.return_value.all.assert_called_once()


def test_get_all_borrows_database_error(borrow_repository, mock_db):
    """Test get_all_borrows when database error occurs."""
    mock_db.query.return_value.all.side_effect = SQLAlchemyError(
        "Database error")

    with pytest.raises(SQLAlchemyError):
        borrow_repository.get_all_borrows(include_returned=True)


def test_get_all_borrows_database_error_with_filter(borrow_repository, mock_db):
    """Test get_all_borrows when database error occurs with filter."""
    mock_db.query.return_value.filter.return_value.all.side_effect = SQLAlchemyError(
        "Database error")

    with pytest.raises(SQLAlchemyError):
        borrow_repository.get_all_borrows(include_returned=False)


def test_get_all_borrows_unexpected_error(borrow_repository, mock_db):
    """Test get_all_borrows when unexpected error occurs."""
    mock_db.query.return_value.all.side_effect = Exception("Unexpected error")

    with pytest.raises(Exception):
        borrow_repository.get_all_borrows(include_returned=True)

"""Unit tests for BorrowRepository data access layer.

Tests cover:
- BorrowRepository initialization
- get_all_borrows() with pagination and filtering
- get_borrow_by_id() for retrieving single records
- create_borrow() for persistence
- return_borrow() for marking returned and restoring availability

Note: Repository layer has NO business logic validation.
All validation is performed in the service layer.
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.borrow_repository import BorrowRepository
from app.schemas.borrow import BorrowBase
from app.models.borrow import BorrowRecord
from app.models.book import Book
from app.common.exceptions import DatabaseError


# ============================================================================
# Test Data Constants
# ============================================================================

BORROW_ID = 1
BOOK_ID = 1
MEMBER_ID = 1
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
def borrow_repository(mock_db):
    """BorrowRepository fixture."""
    return BorrowRepository(mock_db)


# ============================================================================
# Test Data Builders
# ============================================================================


def create_mock_book(book_id: int = BOOK_ID, available: bool = True) -> Book:
    """Create a mock book object."""
    book = MagicMock(spec=Book)
    book.id = book_id
    book.available = available
    return book


def create_mock_borrow_record(
    borrow_id: int = BORROW_ID,
    book_id: int = BOOK_ID,
    member_id: int = MEMBER_ID,
    returned_at: datetime = None,
) -> BorrowRecord:
    """Create a mock borrow record."""
    borrow = MagicMock(spec=BorrowRecord)
    borrow.id = borrow_id
    borrow.book_id = book_id
    borrow.member_id = member_id
    borrow.borrowed_at = datetime(2026, 2, 1)
    borrow.returned_at = returned_at
    return borrow


def create_borrow_request(
    book_id: int = BOOK_ID, member_id: int = MEMBER_ID
) -> BorrowBase:
    """Create a borrow request object."""
    return BorrowBase(book_id=book_id, member_id=member_id)


# ============================================================================
# BorrowRepository Initialization Tests
# ============================================================================


class TestBorrowRepositoryInitialization:
    """Tests for BorrowRepository.__init__()"""

    def test_success(self, mock_db):
        """Test successful initialization with valid database session."""
        repo = BorrowRepository(mock_db)
        assert repo.db == mock_db

    def test_fails_with_none_db(self):
        """Test initialization fails when db is None."""
        with pytest.raises(ValueError) as exc_info:
            BorrowRepository(None)
        assert "Database session cannot be None" in str(exc_info.value)


# ============================================================================
# get_borrow_by_id() Tests
# ============================================================================


class TestGetBorrowById:
    """Tests for BorrowRepository.get_borrow_by_id()"""

    def test_success_finds_borrow(self, borrow_repository, mock_db):
        """Test successful retrieval of existing borrow record."""
        mock_borrow = create_mock_borrow_record()
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_borrow
        mock_db.query.return_value = mock_query

        result = borrow_repository.get_borrow_by_id(BORROW_ID)

        assert result == mock_borrow
        assert result.id == BORROW_ID
        mock_db.query.assert_called_once_with(BorrowRecord)
        mock_query.filter.assert_called_once()

    def test_returns_none_when_not_found(self, borrow_repository, mock_db):
        """Test returns None when borrow record does not exist."""
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        result = borrow_repository.get_borrow_by_id(999)

        assert result is None

    def test_raises_database_error_on_query_failure(self, borrow_repository, mock_db):
        """Test raises DatabaseError when database query fails."""
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = SQLAlchemyError(
            "Connection failed"
        )
        mock_db.query.return_value = mock_query

        with pytest.raises(DatabaseError) as exc_info:
            borrow_repository.get_borrow_by_id(BORROW_ID)
        assert "Failed to retrieve borrow record" in str(exc_info.value)


# ============================================================================
# create_borrow() Tests
# ============================================================================


class TestCreateBorrow:
    """Tests for BorrowRepository.create_borrow()"""

    def test_success(self, borrow_repository, mock_db):
        """Test successful creation of borrow record."""
        borrow_request = create_borrow_request()
        mock_book = create_mock_book(available=True)

        borrow_repository.create_borrow(borrow_request, mock_book)

        # Verify book availability was updated
        assert mock_book.available == False
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_marks_book_unavailable(self, borrow_repository, mock_db):
        """Test that create_borrow marks book as unavailable."""
        borrow_request = create_borrow_request(book_id=10, member_id=5)
        mock_book = create_mock_book(book_id=10, available=True)
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        borrow_repository.create_borrow(borrow_request, mock_book)

        assert mock_book.available == False

    def test_raises_database_error_on_commit_failure(self, borrow_repository, mock_db):
        """Test raises DatabaseError when database commit fails."""
        borrow_request = create_borrow_request()
        mock_book = create_mock_book()
        mock_db.commit.side_effect = SQLAlchemyError("Commit failed")

        with pytest.raises(DatabaseError) as exc_info:
            borrow_repository.create_borrow(borrow_request, mock_book)
        assert "Failed to create borrow record" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

    def test_rolls_back_on_database_error(self, borrow_repository, mock_db):
        """Test rollback is called when database error occurs."""
        borrow_request = create_borrow_request()
        mock_book = create_mock_book()
        mock_db.commit.side_effect = SQLAlchemyError("Error")

        with pytest.raises(DatabaseError):
            borrow_repository.create_borrow(borrow_request, mock_book)
        mock_db.rollback.assert_called_once()


# ============================================================================
# get_all_borrows() Tests
# ============================================================================


class TestGetAllBorrows:
    """Tests for BorrowRepository.get_all_borrows()"""

    def test_success_default_parameters(self, borrow_repository, mock_db):
        """Test successful retrieval with default parameters."""
        mock_borrow = create_mock_borrow_record()
        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.offset.return_value.limit.return_value.all.return_value = [
            mock_borrow
        ]
        mock_db.query.return_value = mock_query

        result, total = borrow_repository.get_all_borrows()

        assert len(result) == 1
        assert total == 1
        assert result[0].id == BORROW_ID

    def test_returns_tuple_with_total_count(self, borrow_repository, mock_db):
        """Test returns tuple of (records, total_count)."""
        borrows = [create_mock_borrow_record(i) for i in range(1, 6)]
        mock_query = MagicMock()
        mock_query.count.return_value = 25
        mock_query.offset.return_value.limit.return_value.all.return_value = (
            borrows
        )
        mock_db.query.return_value = mock_query

        records, total = borrow_repository.get_all_borrows(offset=0, limit=5)

        assert len(records) == 5
        assert total == 25

    def test_success_with_returned_false(self, borrow_repository, mock_db):
        """Test filters only active borrows when returned=False."""
        mock_borrow = create_mock_borrow_record()
        mock_query = MagicMock()
        mock_query.filter.return_value.count.return_value = 1
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_borrow
        ]
        mock_db.query.return_value = mock_query

        result, total = borrow_repository.get_all_borrows(returned=False)

        assert len(result) == 1
        assert total == 1
        mock_query.filter.assert_called()

    def test_success_with_returned_true(self, borrow_repository, mock_db):
        """Test includes all borrows when returned=True (no filter)."""
        active = create_mock_borrow_record()
        returned = create_mock_borrow_record(
            borrow_id=2, returned_at=datetime(2026, 2, 5)
        )
        mock_query = MagicMock()
        mock_query.count.return_value = 2
        mock_query.offset.return_value.limit.return_value.all.return_value = [
            active,
            returned,
        ]
        mock_db.query.return_value = mock_query

        result, total = borrow_repository.get_all_borrows(returned=True)

        assert len(result) == 2
        assert total == 2

    def test_empty_result(self, borrow_repository, mock_db):
        """Test returns empty list with zero total when no records exist."""
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        result, total = borrow_repository.get_all_borrows()

        assert len(result) == 0
        assert total == 0

    def test_pagination_with_custom_offset(self, borrow_repository, mock_db):
        """Test pagination with custom offset and limit."""
        mock_borrow = create_mock_borrow_record()
        mock_query = MagicMock()
        mock_query.count.return_value = 50
        mock_query.offset.return_value.limit.return_value.all.return_value = [
            mock_borrow
        ]
        mock_db.query.return_value = mock_query

        result, total = borrow_repository.get_all_borrows(offset=20, limit=10)

        # Verify offset and limit parameters are passed correctly
        mock_query.offset.assert_called_once_with(20)
        mock_query.offset.return_value.limit.assert_called_once_with(10)
        assert len(result) == 1
        assert total == 50

    def test_pagination_with_zero_offset(self, borrow_repository, mock_db):
        """Test pagination starting from first record."""
        mock_borrow = create_mock_borrow_record()
        mock_query = MagicMock()
        mock_query.count.return_value = 100
        mock_query.offset.return_value.limit.return_value.all.return_value = [
            mock_borrow
        ]
        mock_db.query.return_value = mock_query

        result, total = borrow_repository.get_all_borrows(offset=0, limit=25)

        # Verify offset 0 (first page)
        mock_query.offset.assert_called_once_with(0)
        mock_query.offset.return_value.limit.assert_called_once_with(25)
        assert total == 100

    def test_pagination_large_offset(self, borrow_repository, mock_db):
        """Test pagination with large offset."""
        mock_query = MagicMock()
        mock_query.count.return_value = 500
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        result, total = borrow_repository.get_all_borrows(offset=400, limit=50)

        # Verify large offset applied correctly
        mock_query.offset.assert_called_once_with(400)
        mock_query.offset.return_value.limit.assert_called_once_with(50)
        assert total == 500

    def test_filter_by_member_id(self, borrow_repository, mock_db):
        """Test filters by member_id when provided."""
        mock_borrow = create_mock_borrow_record(member_id=123)
        mock_query = MagicMock()
        mock_query.filter.return_value.count.return_value = 1
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_borrow
        ]
        mock_db.query.return_value = mock_query

        result, _ = borrow_repository.get_all_borrows(member_id=123)

        assert len(result) == 1
        assert result[0].member_id == 123

    def test_filter_by_book_id(self, borrow_repository, mock_db):
        """Test filters by book_id when provided."""
        mock_borrow = create_mock_borrow_record(book_id=456)
        mock_query = MagicMock()
        mock_query.filter.return_value.count.return_value = 1
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_borrow
        ]
        mock_db.query.return_value = mock_query

        result, _ = borrow_repository.get_all_borrows(book_id=456)

        assert len(result) == 1
        assert result[0].book_id == 456

    def test_filter_by_both_ids(self, borrow_repository, mock_db):
        """Test filters by both member_id and book_id."""
        mock_borrow = create_mock_borrow_record(
            member_id=123, book_id=456
        )
        mock_query = MagicMock()
        mock_query.filter.return_value.filter.return_value.count.return_value = 1
        mock_query.filter.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_borrow
        ]
        mock_db.query.return_value = mock_query

        result, _ = borrow_repository.get_all_borrows(
            member_id=123, book_id=456
        )

        assert len(result) == 1
        assert result[0].member_id == 123
        assert result[0].book_id == 456

    def test_raises_database_error_on_query_failure(self, borrow_repository, mock_db):
        """Test raises DatabaseError when database query fails."""
        mock_query = MagicMock()
        mock_query.count.side_effect = SQLAlchemyError("Query failed")
        mock_db.query.return_value = mock_query

        with pytest.raises(DatabaseError) as exc_info:
            borrow_repository.get_all_borrows()
        assert "Failed to retrieve borrow records" in str(exc_info.value)


# ============================================================================
# return_borrow() Tests
# ============================================================================


class TestReturnBorrow:
    """Tests for BorrowRepository.return_borrow()"""

    def test_success(self, borrow_repository, mock_db):
        """Test successful return of borrow record."""
        mock_borrow = create_mock_borrow_record()
        mock_book = create_mock_book()

        borrow_repository.return_borrow(mock_borrow, mock_book)

        # Verify borrow returned_at was set
        assert mock_borrow.returned_at is not None
        # Verify book availability was restored
        assert mock_book.available == True
        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_borrow)

    def test_marks_book_available(self, borrow_repository, mock_db):
        """Test that return_borrow marks book as available."""
        mock_borrow = create_mock_borrow_record()
        mock_book = create_mock_book(available=False)

        borrow_repository.return_borrow(mock_borrow, mock_book)

        assert mock_book.available == True

    def test_sets_returned_at_timestamp(self, borrow_repository, mock_db):
        """Test that return_borrow sets returned_at timestamp."""
        mock_borrow = create_mock_borrow_record(returned_at=None)
        mock_book = create_mock_book()

        borrow_repository.return_borrow(mock_borrow, mock_book)

        assert mock_borrow.returned_at is not None
        assert isinstance(mock_borrow.returned_at, datetime)

    def test_raises_database_error_on_commit_failure(self, borrow_repository, mock_db):
        """Test raises DatabaseError when database commit fails."""
        mock_borrow = create_mock_borrow_record()
        mock_book = create_mock_book()
        mock_db.commit.side_effect = SQLAlchemyError("Commit failed")

        with pytest.raises(DatabaseError) as exc_info:
            borrow_repository.return_borrow(mock_borrow, mock_book)
        assert "Failed to return borrow record" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

    def test_rolls_back_on_database_error(self, borrow_repository, mock_db):
        """Test rollback is called when database error occurs."""
        mock_borrow = create_mock_borrow_record()
        mock_book = create_mock_book()
        mock_db.commit.side_effect = SQLAlchemyError("Error")

        with pytest.raises(DatabaseError):
            borrow_repository.return_borrow(mock_borrow, mock_book)
        mock_db.rollback.assert_called_once()

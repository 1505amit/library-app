"""Unit tests for BorrowService business logic.

Tests cover:
- BorrowService initialization
- borrow_book() with validation and exception handling
- get_all_borrows() with pagination and filtering
- return_borrow() with validation and exception handling

Exception Mapping (from app.common.exceptions):
- BookNotFoundError: Book does not exist
- MemberNotFoundError: Member does not exist
- BorrowNotFoundError: Borrow record does not exist
- InvalidBorrowError: Business rule violation (unavailable, inactive, already returned)
"""
import pytest
from unittest.mock import MagicMock, Mock
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.borrow_service import BorrowService
from app.schemas.borrow import BorrowBase, BorrowDetailedResponse
from app.models.borrow import BorrowRecord
from app.common.exceptions import (
    BookNotFoundError,
    MemberNotFoundError,
    BorrowNotFoundError,
    InvalidBorrowError,
)


# ============================================================================
# Test Data Constants
# ============================================================================

ACTIVE_BORROW_ID = 1
RETURNED_BORROW_ID = 2
BOOK_ID = 1
MEMBER_ID = 1
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
def borrow_service(mock_db):
    """BorrowService fixture with mocked repositories."""
    service = BorrowService(mock_db)
    # Mock all repositories
    service.borrow_repository = MagicMock()
    service.book_repository = MagicMock()
    service.member_repository = MagicMock()
    return service


@pytest.fixture
def borrow_request_data():
    """Sample BorrowBase fixture for borrowing."""
    return BorrowBase(book_id=BOOK_ID, member_id=MEMBER_ID)


# ============================================================================
# Test Data Builders
# ============================================================================


def create_mock_book(book_id: int = BOOK_ID, available: bool = True):
    """Create a mock book object."""
    book = MagicMock()
    book.id = book_id
    book.title = "Test Book"
    book.available = available
    return book


def create_mock_member(member_id: int = MEMBER_ID, active: bool = True):
    """Create a mock member object."""
    member = MagicMock()
    member.id = member_id
    member.name = "Test Member"
    member.active = active
    return member


def create_mock_borrow_record(
    borrow_id: int = ACTIVE_BORROW_ID,
    book_id: int = BOOK_ID,
    member_id: int = MEMBER_ID,
    returned_at: datetime = None,
):
    """Create a mock borrow record object."""
    borrow = MagicMock(spec=BorrowRecord)
    borrow.id = borrow_id
    borrow.book_id = book_id
    borrow.member_id = member_id
    borrow.borrowed_at = datetime(2026, 2, 1)
    borrow.returned_at = returned_at
    return borrow


def create_mock_detailed_borrow_response(
    borrow_id: int = ACTIVE_BORROW_ID,
    book_id: int = BOOK_ID,
    member_id: int = MEMBER_ID,
    returned_at: datetime = None,
):
    """Create a mock detailed borrow response for pagination."""
    return BorrowDetailedResponse(
        id=borrow_id,
        book_id=book_id,
        member_id=member_id,
        borrowed_at=datetime(2026, 2, 1),
        returned_at=returned_at,
        book={
            "id": book_id,
            "title": "Test Book",
            "author": "Test Author",
            "published_year": 2025,
        },
        member={
            "id": member_id,
            "name": "Test Member",
            "email": "test@example.com",
        },
    )


# ============================================================================
# BorrowService Initialization Tests
# ============================================================================


class TestBorrowServiceInitialization:
    """Tests for BorrowService.__init__()"""

    def test_success(self, mock_db):
        """Test successful initialization with valid database session."""
        service = BorrowService(mock_db)
        assert service.db == mock_db
        assert service.borrow_repository is not None
        assert service.book_repository is not None
        assert service.member_repository is not None

    def test_fails_with_none_db(self):
        """Test initialization fails when db is None."""
        with pytest.raises(ValueError) as exc_info:
            BorrowService(None)
        assert "Database session cannot be None" in str(exc_info.value)


# ============================================================================
# borrow_book() Tests
# ============================================================================


class TestBorrowBook:
    """Tests for BorrowService.borrow_book()"""

    def test_success(self, borrow_service, borrow_request_data):
        """Test successful book borrowing."""
        mock_book = create_mock_book(available=True)
        mock_member = create_mock_member(active=True)
        mock_borrow = create_mock_borrow_record()

        borrow_service.book_repository.get_book_by_id.return_value = mock_book
        borrow_service.member_repository.get_member_by_id.return_value = mock_member
        borrow_service.borrow_repository.create_borrow.return_value = mock_borrow

        result = borrow_service.borrow_book(borrow_request_data)

        assert result.id == ACTIVE_BORROW_ID
        assert result.book_id == BOOK_ID
        assert result.member_id == MEMBER_ID
        borrow_service.book_repository.get_book_by_id.assert_called_once_with(
            BOOK_ID)
        borrow_service.member_repository.get_member_by_id.assert_called_once_with(
            MEMBER_ID)
        borrow_service.borrow_repository.create_borrow.assert_called_once_with(
            borrow_request_data, mock_book
        )

    def test_book_not_found(self, borrow_service, borrow_request_data):
        """Test fails when book does not exist."""
        borrow_service.book_repository.get_book_by_id.return_value = None

        with pytest.raises(BookNotFoundError) as exc_info:
            borrow_service.borrow_book(borrow_request_data)
        assert "Book with id 1 not found" in str(exc_info.value)
        borrow_service.book_repository.get_book_by_id.assert_called_once_with(
            BOOK_ID)

    def test_book_not_available(self, borrow_service, borrow_request_data):
        """Test fails when book is not available."""
        mock_book = create_mock_book(available=False)
        borrow_service.book_repository.get_book_by_id.return_value = mock_book

        with pytest.raises(InvalidBorrowError) as exc_info:
            borrow_service.borrow_book(borrow_request_data)
        assert "not available" in str(exc_info.value)

    def test_member_not_found(self, borrow_service, borrow_request_data):
        """Test fails when member does not exist."""
        mock_book = create_mock_book(available=True)
        borrow_service.book_repository.get_book_by_id.return_value = mock_book
        borrow_service.member_repository.get_member_by_id.return_value = None

        with pytest.raises(MemberNotFoundError) as exc_info:
            borrow_service.borrow_book(borrow_request_data)
        assert "Member with id 1 not found" in str(exc_info.value)

    def test_member_not_active(self, borrow_service, borrow_request_data):
        """Test fails when member is inactive."""
        mock_book = create_mock_book(available=True)
        mock_member = create_mock_member(active=False)
        borrow_service.book_repository.get_book_by_id.return_value = mock_book
        borrow_service.member_repository.get_member_by_id.return_value = mock_member

        with pytest.raises(InvalidBorrowError) as exc_info:
            borrow_service.borrow_book(borrow_request_data)
        assert "not active" in str(exc_info.value)


# ============================================================================
# get_all_borrows() Tests
# ============================================================================


class TestGetAllBorrows:
    """Tests for BorrowService.get_all_borrows()"""

    def test_success_default_parameters(self, borrow_service):
        """Test successful retrieval with default parameters."""
        mock_borrow = create_mock_borrow_record()
        borrow_service.borrow_repository.get_all_borrows.return_value = (
            [mock_borrow],
            1,
        )

        result = borrow_service.get_all_borrows()

        assert "data" in result
        assert "pagination" in result
        assert len(result["data"]) == 1
        assert result["pagination"]["total"] == 1
        assert result["pagination"]["page"] == DEFAULT_PAGE
        assert result["pagination"]["limit"] == DEFAULT_LIMIT
        assert result["pagination"]["pages"] == 1

    def test_success_with_returned_true(self, borrow_service):
        """Test retrieval includes both active and returned borrows."""
        active_borrow = create_mock_borrow_record()
        returned_borrow = create_mock_borrow_record(
            borrow_id=RETURNED_BORROW_ID,
            returned_at=datetime(2026, 2, 10),
        )
        borrow_service.borrow_repository.get_all_borrows.return_value = (
            [active_borrow, returned_borrow],
            2,
        )

        result = borrow_service.get_all_borrows(returned=True)

        assert len(result["data"]) == 2
        assert result["data"][0].returned_at is None
        assert result["data"][1].returned_at is not None
        borrow_service.borrow_repository.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=None,
            book_id=None,
            offset=0,
            limit=DEFAULT_LIMIT,
        )

    def test_success_with_returned_false(self, borrow_service):
        """Test retrieval returns only active borrows."""
        mock_borrow = create_mock_borrow_record()
        borrow_service.borrow_repository.get_all_borrows.return_value = (
            [mock_borrow],
            1,
        )

        result = borrow_service.get_all_borrows(returned=False)

        assert len(result["data"]) == 1
        assert result["data"][0].returned_at is None
        borrow_service.borrow_repository.get_all_borrows.assert_called_once_with(
            returned=False,
            member_id=None,
            book_id=None,
            offset=0,
            limit=DEFAULT_LIMIT,
        )

    def test_success_empty_result(self, borrow_service):
        """Test retrieval returns empty list with correct pagination."""
        borrow_service.borrow_repository.get_all_borrows.return_value = ([], 0)

        result = borrow_service.get_all_borrows()

        assert len(result["data"]) == 0
        assert result["pagination"]["total"] == 0
        assert result["pagination"]["pages"] == 0

    def test_success_with_member_filter(self, borrow_service):
        """Test retrieval with member_id filter."""
        mock_borrow = create_mock_borrow_record(member_id=123)
        borrow_service.borrow_repository.get_all_borrows.return_value = (
            [mock_borrow],
            1,
        )

        result = borrow_service.get_all_borrows(member_id=123)

        assert result["data"][0].member_id == 123
        borrow_service.borrow_repository.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=123,
            book_id=None,
            offset=0,
            limit=DEFAULT_LIMIT,
        )

    def test_success_with_book_filter(self, borrow_service):
        """Test retrieval with book_id filter."""
        mock_borrow = create_mock_borrow_record(book_id=456)
        borrow_service.borrow_repository.get_all_borrows.return_value = (
            [mock_borrow],
            1,
        )

        result = borrow_service.get_all_borrows(book_id=456)

        assert result["data"][0].book_id == 456
        borrow_service.borrow_repository.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=None,
            book_id=456,
            offset=0,
            limit=DEFAULT_LIMIT,
        )

    def test_success_with_both_filters(self, borrow_service):
        """Test retrieval with both member and book filters."""
        mock_borrow = create_mock_borrow_record(
            member_id=123, book_id=456
        )
        borrow_service.borrow_repository.get_all_borrows.return_value = (
            [mock_borrow],
            1,
        )

        result = borrow_service.get_all_borrows(member_id=123, book_id=456)

        assert result["data"][0].member_id == 123
        assert result["data"][0].book_id == 456

    def test_success_pagination_multiple_pages(self, borrow_service):
        """Test pagination calculation with multiple pages."""
        borrows = [create_mock_borrow_record() for _ in range(10)]
        borrow_service.borrow_repository.get_all_borrows.return_value = (
            borrows,
            25,
        )

        result = borrow_service.get_all_borrows(page=1, limit=10)

        assert result["pagination"]["total"] == 25
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["limit"] == 10
        assert result["pagination"]["pages"] == 3
        borrow_service.borrow_repository.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=None,
            book_id=None,
            offset=0,
            limit=10,
        )

    def test_success_pagination_second_page(self, borrow_service):
        """Test pagination on second page with correct offset."""
        mock_borrow = create_mock_borrow_record()
        borrow_service.borrow_repository.get_all_borrows.return_value = (
            [mock_borrow],
            25,
        )

        result = borrow_service.get_all_borrows(page=2, limit=10)

        assert result["pagination"]["page"] == 2
        borrow_service.borrow_repository.get_all_borrows.assert_called_once_with(
            returned=True,
            member_id=None,
            book_id=None,
            offset=10,
            limit=10,
        )

    def test_fails_when_page_exceeds_total(self, borrow_service):
        """Test fails when page number exceeds total pages."""
        borrow_service.borrow_repository.get_all_borrows.return_value = ([], 5)

        with pytest.raises(InvalidBorrowError) as exc_info:
            borrow_service.get_all_borrows(page=3, limit=10)
        assert "exceeds total pages" in str(exc_info.value)

    def test_success_when_page_equals_total(self, borrow_service):
        """Test succeeds when page number equals total pages."""
        mock_borrow = create_mock_borrow_record()
        borrow_service.borrow_repository.get_all_borrows.return_value = (
            [mock_borrow],
            5,
        )

        result = borrow_service.get_all_borrows(page=1, limit=10)

        assert result["pagination"]["pages"] == 1
        assert result["pagination"]["page"] == 1


# ============================================================================
# return_borrow() Tests
# ============================================================================


class TestReturnBorrow:
    """Tests for BorrowService.return_borrow()"""

    def test_success(self, borrow_service):
        """Test successful book return."""
        mock_borrow = create_mock_borrow_record(
            returned_at=datetime(2026, 2, 10)
        )
        mock_book = create_mock_book()
        borrow_service.borrow_repository.get_borrow_by_id.return_value = (
            create_mock_borrow_record()
        )
        borrow_service.book_repository.get_book_by_id.return_value = mock_book
        borrow_service.borrow_repository.return_borrow.return_value = mock_borrow

        result = borrow_service.return_borrow(ACTIVE_BORROW_ID)

        assert result.id == ACTIVE_BORROW_ID
        assert result.returned_at is not None
        borrow_service.borrow_repository.get_borrow_by_id.assert_called_once_with(
            ACTIVE_BORROW_ID
        )
        borrow_service.book_repository.get_book_by_id.assert_called_once_with(
            BOOK_ID
        )
        borrow_service.borrow_repository.return_borrow.assert_called_once()

    def test_borrow_not_found(self, borrow_service):
        """Test fails when borrow record does not exist."""
        borrow_service.borrow_repository.get_borrow_by_id.return_value = None

        with pytest.raises(BorrowNotFoundError) as exc_info:
            borrow_service.return_borrow(999)
        assert "Borrow record with id 999 not found" in str(exc_info.value)

    def test_already_returned(self, borrow_service):
        """Test fails when book was already returned."""
        mock_borrow = create_mock_borrow_record(
            returned_at=datetime(2026, 2, 5)
        )
        borrow_service.borrow_repository.get_borrow_by_id.return_value = (
            mock_borrow
        )

        with pytest.raises(InvalidBorrowError) as exc_info:
            borrow_service.return_borrow(ACTIVE_BORROW_ID)
        assert "already been returned" in str(exc_info.value)

    def test_associated_book_not_found(self, borrow_service):
        """Test fails when associated book does not exist."""
        mock_borrow = create_mock_borrow_record()
        borrow_service.borrow_repository.get_borrow_by_id.return_value = (
            mock_borrow
        )
        borrow_service.book_repository.get_book_by_id.return_value = None

        with pytest.raises(BookNotFoundError) as exc_info:
            borrow_service.return_borrow(ACTIVE_BORROW_ID)
        assert "Book with id 1 not found" in str(exc_info.value)

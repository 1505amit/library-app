import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.services.borrow_service import BorrowService
from app.schemas.borrow import BorrowBase, BorrowReturnRequest
from app.models.borrow import BorrowRecord


@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    return MagicMock()


@pytest.fixture
def borrow_service(mock_db):
    """BorrowService fixture."""
    return BorrowService(mock_db)


@pytest.fixture
def borrow_base():
    """Sample BorrowBase fixture."""
    return BorrowBase(book_id=1, member_id=1)


@pytest.fixture
def mock_borrow_record():
    """Mock borrow record fixture."""
    borrow = BorrowRecord()
    borrow.id = 1
    borrow.book_id = 1
    borrow.member_id = 1
    borrow.borrowed_at = datetime.utcnow()
    borrow.returned_at = None
    return borrow


# Test BorrowService initialization
def test_borrow_service_initialization_success(mock_db):
    """Test successful BorrowService initialization."""
    service = BorrowService(mock_db)
    assert service.db == mock_db
    assert service.borrow_repository is not None


def test_borrow_service_initialization_with_none_db():
    """Test BorrowService initialization with None database."""
    with pytest.raises(ValueError) as exc_info:
        BorrowService(None)
    assert "Database session cannot be None" in str(exc_info.value)


# Test borrow_book
def test_borrow_book_success(borrow_service, borrow_base, mock_borrow_record):
    """Test successful book borrowing."""
    borrow_service.borrow_repository.create_borrow = MagicMock(
        return_value=mock_borrow_record)

    result = borrow_service.borrow_book(borrow_base)

    assert result.id == 1
    assert result.book_id == 1
    assert result.member_id == 1
    borrow_service.borrow_repository.create_borrow.assert_called_once_with(
        borrow_base)


def test_borrow_book_validation_error(borrow_service, borrow_base):
    """Test borrow_book when repository raises ValueError."""
    borrow_service.borrow_repository.create_borrow = MagicMock(
        side_effect=ValueError("Book not found")
    )

    with pytest.raises(ValueError) as exc_info:
        borrow_service.borrow_book(borrow_base)
    assert "Book not found" in str(exc_info.value)


def test_borrow_book_database_error(borrow_service, borrow_base):
    """Test borrow_book when repository raises SQLAlchemyError."""
    borrow_service.borrow_repository.create_borrow = MagicMock(
        side_effect=SQLAlchemyError("Database error")
    )

    with pytest.raises(ValueError) as exc_info:
        borrow_service.borrow_book(borrow_base)
    assert "Failed to borrow book from database" in str(exc_info.value)


def test_borrow_book_unexpected_error(borrow_service, borrow_base):
    """Test borrow_book when repository raises unexpected exception."""
    borrow_service.borrow_repository.create_borrow = MagicMock(
        side_effect=Exception("Unexpected error")
    )

    with pytest.raises(Exception):
        borrow_service.borrow_book(borrow_base)

# Test get_all_borrows


def test_get_all_borrows_success_with_all_records(borrow_service):
    """Test get_all_borrows returns all records when include_returned=True."""
    mock_active_borrow = MagicMock(spec=BorrowRecord)
    mock_active_borrow.id = 1
    mock_active_borrow.returned_at = None

    mock_returned_borrow = MagicMock(spec=BorrowRecord)
    mock_returned_borrow.id = 2
    mock_returned_borrow.returned_at = datetime.utcnow()

    borrow_service.borrow_repository.get_all_borrows = MagicMock(
        return_value=[mock_active_borrow, mock_returned_borrow]
    )

    result = borrow_service.get_all_borrows(include_returned=True)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2
    borrow_service.borrow_repository.get_all_borrows.assert_called_once_with(
        include_returned=True
    )


def test_get_all_borrows_success_active_only(borrow_service):
    """Test get_all_borrows returns only active records when include_returned=False."""
    mock_active_borrow = MagicMock(spec=BorrowRecord)
    mock_active_borrow.id = 1
    mock_active_borrow.returned_at = None

    borrow_service.borrow_repository.get_all_borrows = MagicMock(
        return_value=[mock_active_borrow]
    )

    result = borrow_service.get_all_borrows(include_returned=False)

    assert len(result) == 1
    assert result[0].id == 1
    borrow_service.borrow_repository.get_all_borrows.assert_called_once_with(
        include_returned=False
    )


def test_get_all_borrows_empty_list(borrow_service):
    """Test get_all_borrows returns empty list when no records exist."""
    borrow_service.borrow_repository.get_all_borrows = MagicMock(
        return_value=[]
    )

    result = borrow_service.get_all_borrows(include_returned=True)

    assert len(result) == 0
    borrow_service.borrow_repository.get_all_borrows.assert_called_once_with(
        include_returned=True
    )


def test_get_all_borrows_database_error(borrow_service):
    """Test get_all_borrows when repository raises SQLAlchemyError."""
    borrow_service.borrow_repository.get_all_borrows = MagicMock(
        side_effect=SQLAlchemyError("Database error")
    )

    with pytest.raises(ValueError) as exc_info:
        borrow_service.get_all_borrows(include_returned=True)
    assert "Failed to retrieve borrow records from database" in str(
        exc_info.value)


def test_get_all_borrows_unexpected_error(borrow_service):
    """Test get_all_borrows when repository raises unexpected exception."""
    borrow_service.borrow_repository.get_all_borrows = MagicMock(
        side_effect=Exception("Unexpected error")
    )

    with pytest.raises(Exception):
        borrow_service.get_all_borrows(include_returned=True)

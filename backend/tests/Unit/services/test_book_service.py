"""Unit tests for BookService business logic.

Tests cover:
- BookService initialization
- get_all_books() with pagination and validation
- get_book_by_id() for retrieving single books
- create_book() with validation and exception handling
- update_book() with validation and exception handling

Exception Mapping (from app.common.exceptions):
- BookNotFoundError: Book does not exist
- InvalidBookError: Business rule violation (published_year > 2026)
- DatabaseError: Database operation failures
"""
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.book_service import BookService
from app.schemas.book import BookBase
from app.models.book import Book
from app.common.exceptions import (
    BookNotFoundError,
    InvalidBookError,
    DatabaseError,
)


# ============================================================================
# Test Data Constants
# ============================================================================

BOOK_ID = 1
BOOK_TITLE = "Test Book"
BOOK_AUTHOR = "Test Author"
BOOK_YEAR = 2025
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
def book_service(mock_db):
    """BookService fixture with mocked repositories."""
    service = BookService(mock_db)
    # Mock the repository
    service.books_repository = MagicMock()
    return service


# ============================================================================
# Test Data Builders
# ============================================================================

def create_mock_book(
    book_id: int = BOOK_ID,
    title: str = BOOK_TITLE,
    author: str = BOOK_AUTHOR,
    published_year: int = BOOK_YEAR,
    available: bool = True,
):
    """Create a mock book object."""
    book = MagicMock(spec=Book)
    book.id = book_id
    book.title = title
    book.author = author
    book.published_year = published_year
    book.available = available
    return book


def create_book_request(
    title: str = BOOK_TITLE,
    author: str = BOOK_AUTHOR,
    published_year: int = BOOK_YEAR,
    available: bool = True,
):
    """Create a book request object."""
    return BookBase(title=title, author=author, published_year=published_year, available=available)


def create_paginated_book_response(
    books: list,
    page: int = DEFAULT_PAGE,
    limit: int = DEFAULT_LIMIT,
    total: int = None,
):
    """Create a paginated book response."""
    if total is None:
        total = len(books)
    pages = (total + limit - 1) // limit
    return {
        "data": books,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        }
    }


# ============================================================================
# BookService Initialization Tests
# ============================================================================

class TestBookServiceInitialization:
    """Tests for BookService.__init__()"""

    def test_success(self, mock_db):
        """Test successful initialization with valid database session."""
        service = BookService(mock_db)

        assert service.db == mock_db
        assert service.books_repository is not None

    def test_fails_with_none_db(self):
        """Test initialization fails when db is None."""
        with pytest.raises(ValueError) as exc_info:
            BookService(None)
        assert "Database session cannot be None" in str(exc_info.value)

# ============================================================================
# get_book_by_id() Tests
# ============================================================================


class TestGetBookById:
    """Tests for BookService.get_book_by_id()"""

    def test_success(self, book_service):
        """Test successful retrieval of book by ID."""
        mock_book = create_mock_book()
        book_service.books_repository.get_book_by_id.return_value = mock_book

        result = book_service.get_book_by_id(BOOK_ID)

        assert result.id == BOOK_ID
        assert result.title == BOOK_TITLE
        assert result.author == BOOK_AUTHOR
        book_service.books_repository.get_book_by_id.assert_called_once_with(
            BOOK_ID)

    def test_fails_when_book_not_found(self, book_service):
        """Test fails when book does not exist."""
        book_service.books_repository.get_book_by_id.return_value = None

        with pytest.raises(BookNotFoundError) as exc_info:
            book_service.get_book_by_id(999)
        assert "Book with id 999 not found" in str(exc_info.value)

    def test_raises_database_error_on_query_failure(self, book_service):
        """Test raises DatabaseError when database query fails."""
        book_service.books_repository.get_book_by_id.side_effect = DatabaseError(
            "Query failed")

        with pytest.raises(DatabaseError) as exc_info:
            book_service.get_book_by_id(BOOK_ID)
        assert "Query failed" in str(exc_info.value)


# ============================================================================
# create_book() Tests
# ============================================================================

class TestCreateBook:
    """Tests for BookService.create_book()"""

    def test_success(self, book_service):
        """Test successful book creation."""
        book_request = create_book_request()
        mock_book = create_mock_book()
        book_service.books_repository.create_book.return_value = mock_book

        result = book_service.create_book(book_request)

        assert result.id == BOOK_ID
        assert result.title == BOOK_TITLE
        book_service.books_repository.create_book.assert_called_once_with(
            book_request)

    def test_success_with_unavailable_book(self, book_service):
        """Test successful creation with unavailable book."""
        book_request = create_book_request(available=False)
        mock_book = create_mock_book(available=False)
        book_service.books_repository.create_book.return_value = mock_book

        result = book_service.create_book(book_request)

        assert result.available is False
        book_service.books_repository.create_book.assert_called_once_with(
            book_request)

    def test_fails_with_future_published_year(self, book_service):
        """Test fails when published_year is in the future (> 2026)."""
        book_request = create_book_request(published_year=2027)

        with pytest.raises(InvalidBookError) as exc_info:
            book_service.create_book(book_request)
        assert "Published year cannot be in the future" in str(exc_info.value)
        book_service.books_repository.create_book.assert_not_called()

    def test_succeeds_with_year_2026(self, book_service):
        """Test succeeds with published_year = 2026 (boundary)."""
        book_request = create_book_request(published_year=2026)
        mock_book = create_mock_book(published_year=2026)
        book_service.books_repository.create_book.return_value = mock_book

        result = book_service.create_book(book_request)

        assert result.published_year == 2026
        book_service.books_repository.create_book.assert_called_once()

    def test_fails_with_old_year(self, book_service):
        """Test succeeds with very old published_year (no lower bound)."""
        book_request = create_book_request(published_year=1000)
        mock_book = create_mock_book(published_year=1000)
        book_service.books_repository.create_book.return_value = mock_book

        result = book_service.create_book(book_request)

        assert result.published_year == 1000

    def test_raises_database_error_on_creation_failure(self, book_service):
        """Test raises DatabaseError when database operation fails."""
        book_request = create_book_request()
        book_service.books_repository.create_book.side_effect = DatabaseError(
            "Failed to create book in database")

        with pytest.raises(DatabaseError) as exc_info:
            book_service.create_book(book_request)
        assert "Failed to create book" in str(exc_info.value)


# ============================================================================
# get_all_books() Tests
# ============================================================================

class TestGetAllBooks:
    """Tests for BookService.get_all_books()"""

    def test_success_default_parameters(self, book_service):
        """Test successful retrieval with default parameters."""
        mock_book = create_mock_book()
        book_service.books_repository.get_all_books.return_value = (
            [mock_book],
            1,
        )

        result = book_service.get_all_books()

        assert "data" in result
        assert "pagination" in result
        assert len(result["data"]) == 1
        assert result["data"][0].id == BOOK_ID
        assert result["pagination"]["total"] == 1
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["limit"] == 10
        assert result["pagination"]["pages"] == 1
        book_service.books_repository.get_all_books.assert_called_once_with(
            offset=0, limit=10)

    def test_success_with_custom_page(self, book_service):
        """Test successful retrieval with custom page."""
        books = [create_mock_book(i) for i in range(2, 7)]
        book_service.books_repository.get_all_books.return_value = (
            books,
            25,
        )

        result = book_service.get_all_books(page=3, limit=5)

        assert len(result["data"]) == 5
        assert result["pagination"]["total"] == 25
        assert result["pagination"]["page"] == 3
        assert result["pagination"]["limit"] == 5
        assert result["pagination"]["pages"] == 5
        book_service.books_repository.get_all_books.assert_called_once_with(
            offset=10, limit=5)

    def test_success_has_proper_response_structure(self, book_service):
        """Test response has data and pagination keys."""
        mock_book = create_mock_book()
        book_service.books_repository.get_all_books.return_value = (
            [mock_book],
            1,
        )

        result = book_service.get_all_books()

        assert isinstance(result, dict)
        assert set(result.keys()) == {"data", "pagination"}
        assert isinstance(result["data"], list)
        assert isinstance(result["pagination"], dict)

    def test_empty_result(self, book_service):
        """Test retrieval when no books exist."""
        book_service.books_repository.get_all_books.return_value = ([], 0)

        result = book_service.get_all_books()

        assert result["data"] == []
        assert result["pagination"]["total"] == 0
        assert result["pagination"]["pages"] == 0

    def test_pagination_offset_calculation(self, book_service):
        """Test pagination offset is calculated correctly from page."""
        book_service.books_repository.get_all_books.return_value = ([], 0)

        # Page 1 should have offset 0
        book_service.get_all_books(page=1, limit=10)
        book_service.books_repository.get_all_books.assert_called_with(
            offset=0, limit=10)

        book_service.books_repository.reset_mock()
        book_service.books_repository.get_all_books.return_value = ([], 0)

        # Page 2 should have offset 10
        book_service.get_all_books(page=2, limit=10)
        book_service.books_repository.get_all_books.assert_called_with(
            offset=10, limit=10)

        book_service.books_repository.reset_mock()
        book_service.books_repository.get_all_books.return_value = ([], 0)

        # Page 5 should have offset 40
        book_service.get_all_books(page=5, limit=10)
        book_service.books_repository.get_all_books.assert_called_with(
            offset=40, limit=10)

    def test_fails_when_page_exceeds_total_pages(self, book_service):
        """Test fails when requested page exceeds total pages."""
        # Total 25 books, 10 per page = 3 pages total
        book_service.books_repository.get_all_books.return_value = ([], 25)

        with pytest.raises(InvalidBookError) as exc_info:
            book_service.get_all_books(page=5, limit=10)
        assert "exceeds total pages" in str(exc_info.value)

    def test_succeeds_on_exact_last_page(self, book_service):
        """Test succeeds when page equals total pages."""
        books = [create_mock_book(i) for i in range(21, 26)]
        book_service.books_repository.get_all_books.return_value = (
            books,
            25,
        )

        result = book_service.get_all_books(page=3, limit=10)

        assert len(result["data"]) == 5
        assert result["pagination"]["pages"] == 3

    def test_raises_database_error_on_query_failure(self, book_service):
        """Test raises DatabaseError when database query fails."""
        book_service.books_repository.get_all_books.side_effect = DatabaseError(
            "Query failed")

        with pytest.raises(DatabaseError) as exc_info:
            book_service.get_all_books()
        assert "Query failed" in str(exc_info.value)


# ============================================================================
# update_book() Tests
# ============================================================================

class TestUpdateBook:
    """Tests for BookService.update_book()"""

    def test_success(self, book_service):
        """Test successful book update."""
        book_request = create_book_request()
        mock_book = create_mock_book()
        book_service.books_repository.get_book_by_id.return_value = mock_book
        book_service.books_repository.update_book.return_value = mock_book

        result = book_service.update_book(BOOK_ID, book_request)

        assert result.id == BOOK_ID
        book_service.books_repository.get_book_by_id.assert_called_once_with(
            BOOK_ID)
        book_service.books_repository.update_book.assert_called_once_with(
            BOOK_ID, book_request, mock_book)

    def test_success_updates_title_only(self, book_service):
        """Test successful update changing only title."""
        updated_request = create_book_request(title="Updated Title")
        mock_book = create_mock_book()
        book_service.books_repository.get_book_by_id.return_value = mock_book
        book_service.books_repository.update_book.return_value = mock_book

        result = book_service.update_book(BOOK_ID, updated_request)

        assert result.id == BOOK_ID
        book_service.books_repository.update_book.assert_called_once_with(
            BOOK_ID, updated_request, mock_book)

    def test_success_updates_availability(self, book_service):
        """Test successful update changing availability."""
        updated_request = create_book_request(available=False)
        mock_book = create_mock_book(available=False)
        book_service.books_repository.get_book_by_id.return_value = mock_book
        book_service.books_repository.update_book.return_value = mock_book

        result = book_service.update_book(BOOK_ID, updated_request)

        assert result.available is False

    def test_fails_when_book_not_found(self, book_service):
        """Test fails when book does not exist."""
        book_request = create_book_request()
        book_service.books_repository.get_book_by_id.return_value = None

        with pytest.raises(BookNotFoundError) as exc_info:
            book_service.update_book(999, book_request)
        assert "Book with id 999 not found" in str(exc_info.value)

    def test_fails_with_future_published_year(self, book_service):
        """Test fails when attempting to update with future published_year."""
        book_request = create_book_request(published_year=2027)
        mock_book = create_mock_book()
        book_service.books_repository.get_book_by_id.return_value = mock_book

        with pytest.raises(InvalidBookError) as exc_info:
            book_service.update_book(BOOK_ID, book_request)
        assert "Published year cannot be in the future" in str(exc_info.value)
        book_service.books_repository.update_book.assert_not_called()

    def test_raises_database_error_on_update_failure(self, book_service):
        """Test raises DatabaseError when database operation fails."""
        book_request = create_book_request()
        mock_book = create_mock_book()
        book_service.books_repository.get_book_by_id.return_value = mock_book
        book_service.books_repository.update_book.side_effect = DatabaseError(
            "Failed to update book in database")

        with pytest.raises(DatabaseError) as exc_info:
            book_service.update_book(BOOK_ID, book_request)
        assert "Failed to update book" in str(exc_info.value)

"""Unit tests for BookRepository data access layer.

Tests cover:
- BookRepository initialization
- get_all_books() with pagination
- get_book_by_id() for retrieving single books
- create_book() for persistence
- update_book() for updating existing books

Note: Repository layer has NO business logic validation.
All validation is performed in the service layer.
"""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.repositories.book_repository import BookRepository
from app.schemas.book import BookBase
from app.models.book import Book
from app.common.exceptions import DatabaseError


# ============================================================================
# Test Data Constants
# ============================================================================

BOOK_ID = 1
BOOK_TITLE = "Test Book"
BOOK_AUTHOR = "Test Author"
BOOK_YEAR = 2025
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
def book_repository(mock_db):
    """BookRepository fixture."""
    return BookRepository(mock_db)


# ============================================================================
# Test Data Builders
# ============================================================================

def create_mock_book(
    book_id: int = BOOK_ID,
    title: str = BOOK_TITLE,
    author: str = BOOK_AUTHOR,
    published_year: int = BOOK_YEAR,
    available: bool = True,
) -> Book:
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
) -> BookBase:
    """Create a book request object."""
    return BookBase(title=title, author=author, published_year=published_year, available=available)


# ============================================================================
# BookRepository Initialization Tests
# ============================================================================

class TestBookRepositoryInitialization:
    """Tests for BookRepository.__init__()"""

    def test_success(self, mock_db):
        """Test successful initialization with valid database session."""
        repo = BookRepository(mock_db)
        assert repo.db == mock_db

    def test_fails_with_none_db(self):
        """Test fails when database session is None."""
        with pytest.raises(ValueError) as exc_info:
            BookRepository(None)
        assert "Database session cannot be None" in str(exc_info.value)


# ============================================================================
# get_book_by_id() Tests
# ============================================================================

class TestGetBookById:
    """Tests for BookRepository.get_book_by_id()"""

    def test_success(self, book_repository, mock_db):
        """Test successful retrieval of book by ID."""
        mock_book = create_mock_book()
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_book
        mock_db.query.return_value = mock_query

        result = book_repository.get_book_by_id(BOOK_ID)

        assert result.id == BOOK_ID
        assert result.title == BOOK_TITLE
        mock_db.query.assert_called_once_with(Book)

    def test_returns_none_when_not_found(self, book_repository, mock_db):
        """Test returns None when book does not exist."""
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        result = book_repository.get_book_by_id(999)

        assert result is None

    def test_raises_database_error_on_query_failure(self, book_repository, mock_db):
        """Test raises DatabaseError when database query fails."""
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = SQLAlchemyError(
            "Query failed")
        mock_db.query.return_value = mock_query

        with pytest.raises(DatabaseError) as exc_info:
            book_repository.get_book_by_id(BOOK_ID)
        assert "Failed to retrieve book" in str(exc_info.value)


# ============================================================================
# create_book() Tests
# ============================================================================

class TestCreateBook:
    """Tests for BookRepository.create_book()"""

    def test_success(self, book_repository, mock_db):
        """Test successful book creation."""
        book_request = create_book_request()
        mock_book = create_mock_book()

        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Mock Book class to track calls
        with patch('app.repositories.book_repository.Book') as mock_book_class:
            mock_book_class.return_value = mock_book
            result = book_repository.create_book(book_request)

        assert result.id == BOOK_ID
        assert result.title == BOOK_TITLE
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_book)

    def test_success_unavailable_book(self, book_repository, mock_db):
        """Test successful creation with unavailable book."""
        book_request = create_book_request(available=False)
        mock_book = create_mock_book(available=False)

        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        with patch('app.repositories.book_repository.Book') as mock_book_class:
            mock_book_class.return_value = mock_book
            result = book_repository.create_book(book_request)

        assert result.available is False
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_raises_database_error_on_sqlalchemy_error(self, book_repository, mock_db):
        """Test raises DatabaseError when SQLAlchemy error occurs."""
        book_request = create_book_request()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock(
            side_effect=SQLAlchemyError("Constraint violation"))
        mock_db.rollback = MagicMock()

        with patch('app.repositories.book_repository.Book'):
            with pytest.raises(DatabaseError) as exc_info:
                book_repository.create_book(book_request)
            assert "Failed to create book" in str(exc_info.value)
        mock_db.rollback.assert_called_once()


# ============================================================================
# get_all_books() Tests
# ============================================================================

class TestGetAllBooks:
    """Tests for BookRepository.get_all_books()"""

    def test_success_default_parameters(self, book_repository, mock_db):
        """Test successful retrieval with default pagination."""
        mock_book = create_mock_book()
        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_book]
        mock_db.query.return_value = mock_query

        result, total = book_repository.get_all_books()

        assert len(result) == 1
        assert total == 1
        assert result[0].id == BOOK_ID
        mock_query.order_by.return_value.offset.assert_called_once_with(0)
        mock_query.order_by.return_value.offset.return_value.limit.assert_called_once_with(
            10)

    def test_returns_tuple_with_total_count(self, book_repository, mock_db):
        """Test returns tuple of (books, total_count)."""
        books = [create_mock_book(i) for i in range(1, 6)]
        mock_query = MagicMock()
        mock_query.count.return_value = 25
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = books
        mock_db.query.return_value = mock_query

        records, total = book_repository.get_all_books(offset=0, limit=5)

        assert len(records) == 5
        assert total == 25

    def test_empty_result(self, book_repository, mock_db):
        """Test returns empty list when no books exist."""
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        result, total = book_repository.get_all_books()

        assert len(result) == 0
        assert total == 0

    def test_pagination_with_custom_offset(self, book_repository, mock_db):
        """Test pagination with custom offset and limit."""
        mock_book = create_mock_book()
        mock_query = MagicMock()
        mock_query.count.return_value = 50
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_book]
        mock_db.query.return_value = mock_query

        result, total = book_repository.get_all_books(offset=20, limit=10)

        mock_query.order_by.return_value.offset.assert_called_once_with(20)
        mock_query.order_by.return_value.offset.return_value.limit.assert_called_once_with(
            10)
        assert total == 50

    def test_pagination_large_offset(self, book_repository, mock_db):
        """Test pagination with large offset."""
        mock_query = MagicMock()
        mock_query.count.return_value = 500
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        result, total = book_repository.get_all_books(offset=400, limit=50)

        mock_query.order_by.return_value.offset.assert_called_once_with(400)
        mock_query.order_by.return_value.offset.return_value.limit.assert_called_once_with(
            50)
        assert total == 500

    def test_raises_database_error_on_query_failure(self, book_repository, mock_db):
        """Test raises DatabaseError when database query fails."""
        mock_query = MagicMock()
        mock_query.count.side_effect = SQLAlchemyError("Query failed")
        mock_db.query.return_value = mock_query

        with pytest.raises(DatabaseError) as exc_info:
            book_repository.get_all_books()
        assert "Failed to retrieve books" in str(exc_info.value)


# ============================================================================
# update_book() Tests
# ============================================================================

class TestUpdateBook:
    """Tests for BookRepository.update_book()"""

    def test_success(self, book_repository, mock_db):
        """Test successful book update."""
        book_request = create_book_request()
        mock_book = create_mock_book()

        book_repository.update_book(BOOK_ID, book_request, mock_book)

        # Verify attributes were set
        assert mock_book.title == BOOK_TITLE
        assert mock_book.author == BOOK_AUTHOR
        assert mock_book.published_year == BOOK_YEAR
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_book)

    def test_updates_specific_fields(self, book_repository, mock_db):
        """Test update sets correct fields on book object."""
        update_data = BookBase(
            title="Updated Title",
            author="Updated Author",
            published_year=2026,
            available=False,
        )
        mock_book = create_mock_book()

        book_repository.update_book(BOOK_ID, update_data, mock_book)

        assert mock_book.title == "Updated Title"
        assert mock_book.author == "Updated Author"
        assert mock_book.published_year == 2026
        assert mock_book.available is False

    def test_updates_availability(self, book_repository, mock_db):
        """Test update availability flag."""
        update_data = BookBase(
            title=BOOK_TITLE,
            author=BOOK_AUTHOR,
            published_year=BOOK_YEAR,
            available=False,
        )
        mock_book = create_mock_book(available=True)

        book_repository.update_book(BOOK_ID, update_data, mock_book)

        assert mock_book.available is False
        mock_db.commit.assert_called_once()

    def test_raises_database_error_on_sqlalchemy_error(self, book_repository, mock_db):
        """Test raises DatabaseError when SQLAlchemy error occurs."""
        book_request = create_book_request()
        mock_book = create_mock_book()
        mock_db.commit.side_effect = SQLAlchemyError("Database error")
        mock_db.rollback = MagicMock()

        with pytest.raises(DatabaseError) as exc_info:
            book_repository.update_book(BOOK_ID, book_request, mock_book)
        assert "Failed to update book" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

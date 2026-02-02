import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError

from app.services.book_service import BookService
from app.schemas.book import BookResponse


@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    return MagicMock()


@pytest.fixture
def book_service(mock_db):
    """BookService fixture with mocked repository."""
    service = BookService(mock_db)
    service.books_repository = MagicMock()
    return service

def test_init_success(mock_db):
    """Test BookService initializes successfully with valid db."""
    service = BookService(mock_db)
    assert service.db == mock_db
    assert service.books_repository is not None

def test_init_with_none_db():
    """Test BookService initialization fails with None database."""
    with pytest.raises(ValueError) as exc_info:
        BookService(None)
    assert "Database session cannot be None" in str(exc_info.value)

def test_get_all_books_success(book_service):
    """Test get_all_books returns books successfully."""
    mock_books = [
        BookResponse(id=1, title="Book 1", author="Author 1", published_year=2020, available=True),
        BookResponse(id=2, title="Book 2", author="Author 2", published_year=2021, available=False),
    ]
    book_service.books_repository.get_all_books.return_value = mock_books

    result = book_service.get_all_books()

    assert result == mock_books
    assert len(result) == 2
    book_service.books_repository.get_all_books.assert_called_once()

def test_get_all_books_empty(book_service):
    """Test get_all_books returns empty list when no books exist."""
    book_service.books_repository.get_all_books.return_value = []

    result = book_service.get_all_books()

    assert result == []
    assert len(result) == 0
    book_service.books_repository.get_all_books.assert_called_once()

def test_get_all_books_database_error(book_service):
    """Test get_all_books raises ValueError on SQLAlchemy error."""
    book_service.books_repository.get_all_books.side_effect = SQLAlchemyError("DB connection error")

    with pytest.raises(ValueError) as exc_info:
        book_service.get_all_books()
    assert "Failed to retrieve books from database" in str(exc_info.value)

def test_get_all_books_generic_exception(book_service):
    """Test get_all_books re-raises generic exceptions."""
    book_service.books_repository.get_all_books.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(RuntimeError):
        book_service.get_all_books()

def test_create_book_success(book_service):
    """Test create_book successfully creates and returns a book."""
    from app.schemas.book import BookBase
    new_book = BookBase(title="New Book", author="Author", published_year=2024, available=True)
    created_book = BookResponse(id=1, title="New Book", author="Author", published_year=2024, available=True)
    book_service.books_repository.create_book.return_value = created_book

    result = book_service.create_book(new_book)

    assert result == created_book
    assert result.id == 1
    assert result.title == "New Book"
    book_service.books_repository.create_book.assert_called_once_with(new_book)

def test_create_book_database_error(book_service):
    """Test create_book raises ValueError on SQLAlchemy error."""
    from app.schemas.book import BookBase
    new_book = BookBase(title="New Book", author="Author", published_year=2024, available=True)
    book_service.books_repository.create_book.side_effect = SQLAlchemyError("DB constraint violation")

    with pytest.raises(ValueError) as exc_info:
        book_service.create_book(new_book)
    assert "Failed to create book in database" in str(exc_info.value)

def test_create_book_generic_exception(book_service):
    """Test create_book re-raises generic exceptions."""
    from app.schemas.book import BookBase
    new_book = BookBase(title="New Book", author="Author", published_year=2024, available=True)
    book_service.books_repository.create_book.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(RuntimeError):
        book_service.create_book(new_book)

def test_update_book_success(book_service):
    """Test update_book successfully updates and returns a book."""
    from app.schemas.book import BookBase
    book_id = 1
    update_data = BookBase(title="Updated", author="Updated Author", published_year=2024, available=True)
    updated_book = BookResponse(id=1, **update_data.dict())
    book_service.books_repository.update_book.return_value = updated_book

    result = book_service.update_book(book_id, update_data)

    assert result == updated_book
    assert result.title == "Updated"
    assert result.id == 1
    book_service.books_repository.update_book.assert_called_once_with(book_id, update_data)

def test_update_book_not_found(book_service):
    """Test update_book raises ValueError when book not found."""
    from app.schemas.book import BookBase
    book_id = 999
    update_data = BookBase(title="Updated", author="Author", published_year=2024, available=True)
    book_service.books_repository.update_book.side_effect = ValueError(f"Book with id {book_id} not found")

    with pytest.raises(ValueError) as exc_info:
        book_service.update_book(book_id, update_data)
    assert "not found" in str(exc_info.value)

def test_update_book_database_error(book_service):
    """Test update_book raises ValueError on SQLAlchemy error."""
    from app.schemas.book import BookBase
    book_id = 1
    update_data = BookBase(title="Updated", author="Author", published_year=2024, available=True)
    book_service.books_repository.update_book.side_effect = SQLAlchemyError("DB constraint violation")

    with pytest.raises(ValueError) as exc_info:
        book_service.update_book(book_id, update_data)
    assert "Failed to update book in database" in str(exc_info.value)

def test_update_book_generic_exception(book_service):
    """Test update_book re-raises generic exceptions."""
    from app.schemas.book import BookBase
    book_id = 1
    update_data = BookBase(title="Updated", author="Author", published_year=2024, available=True)
    book_service.books_repository.update_book.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(RuntimeError):
        book_service.update_book(book_id, update_data)

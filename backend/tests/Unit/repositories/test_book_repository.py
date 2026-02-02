import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.book_repository import BookRepository
from app.models.book import Book


@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    return MagicMock()


@pytest.fixture
def repository(mock_db):
    """BookRepository fixture."""
    return BookRepository(mock_db)


def test_init_success(mock_db):
    """Test repo initializes successfully with valid db."""
    repo = BookRepository(mock_db)
    assert repo.db == mock_db

def test_init_with_none_db():
    """Test repo initialization fails with None database."""
    with pytest.raises(ValueError) as exc_info:
        BookRepository(None)
    assert "Database session cannot be None" in str(exc_info.value)


def test_get_all_books_success(repository, mock_db):
    """Test get_all_books returns all books successfully."""
    # Setup mock books
    mock_book1 = MagicMock(spec=Book)
    mock_book1.id = 1
    mock_book1.title = "Book 1"

    mock_book2 = MagicMock(spec=Book)
    mock_book2.id = 2
    mock_book2.title = "Book 2"

    mock_db.query.return_value.all.return_value = [mock_book1, mock_book2]

    result = repository.get_all_books()

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2
    mock_db.query.assert_called_once()

def test_get_all_books_empty(repository, mock_db):
    """Test get_all_books returns empty list when no books exist."""
    mock_db.query.return_value.all.return_value = []

    result = repository.get_all_books()

    assert result == []
    mock_db.query.assert_called_once()

def test_get_all_books_database_error(repository, mock_db):
    """Test get_all_books raises SQLAlchemy error on db failure."""
    mock_db.query.side_effect = SQLAlchemyError("Connection failed")

    with pytest.raises(SQLAlchemyError):
        repository.get_all_books()

def test_get_all_books_unexpected_error(repository, mock_db):
    """Test get_all_books raises generic exceptions."""
    mock_db.query.side_effect = Exception("Unexpected error")

    with pytest.raises(Exception):
        repository.get_all_books()

def test_create_book_success(repository, mock_db):
    """Test create_book successfully creates and returns a book."""
    from app.schemas.book import BookBase

    new_book = BookBase(title="New Book", author="Author", published_year=2024, available=True)
    db_book = MagicMock(spec=Book)
    db_book.id = 1
    db_book.title = "New Book"
    db_book.author = "Author"
    db_book.published_year = 2024
    db_book.available = True

    # Mock the db.add, db.commit, db.refresh
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock(side_effect=lambda obj: None)

    # Mock Book class constructor
    with patch('app.repositories.book_repository.Book') as mock_book_class:
        mock_book_class.return_value = db_book

        result = repository.create_book(new_book)

    assert result == db_book
    assert result.id == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_book_database_error(repository, mock_db):
    """Test create_book rolls back and re-raises SQLAlchemy error."""
    from app.schemas.book import BookBase

    new_book = BookBase(title="New Book", author="Author", published_year=2024, available=True)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock(side_effect=SQLAlchemyError("Constraint violation"))
    mock_db.rollback = MagicMock()

    with patch('app.repositories.book_repository.Book'):
        with pytest.raises(SQLAlchemyError):
            repository.create_book(new_book)

    mock_db.rollback.assert_called_once()

def test_create_book_unexpected_error(repository, mock_db):
    """Test create_book rolls back and re-raises generic exceptions."""
    from app.schemas.book import BookBase

    new_book = BookBase(title="New Book", author="Author", published_year=2024, available=True)
    mock_db.add = MagicMock(side_effect=RuntimeError("Unexpected error"))
    mock_db.rollback = MagicMock()

    with patch('app.repositories.book_repository.Book'):
        with pytest.raises(RuntimeError):
            repository.create_book(new_book)

    mock_db.rollback.assert_called_once()

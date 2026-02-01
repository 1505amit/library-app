import pytest
from unittest.mock import MagicMock
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

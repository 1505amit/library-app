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


def test_get_book_by_id_success(repository, mock_db):
    """Test get_book_by_id successfully retrieves a book."""
    book_id = 1
    mock_book = MagicMock(spec=Book)
    mock_book.id = 1
    mock_book.title = "Book 1"

    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = mock_book
    mock_db.query.return_value = query_mock

    result = repository.get_book_by_id(book_id)

    assert result == mock_book
    assert result.id == 1
    assert result.title == "Book 1"
    mock_db.query.assert_called_once()

def test_get_book_by_id_not_found(repository, mock_db):
    """Test get_book_by_id raises ValueError when book not found."""
    book_id = 999

    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = None
    mock_db.query.return_value = query_mock

    with pytest.raises(ValueError) as exc_info:
        repository.get_book_by_id(book_id)
    assert "not found" in str(exc_info.value)

def test_get_book_by_id_database_error(repository, mock_db):
    """Test get_book_by_id raises SQLAlchemy error on db failure."""
    book_id = 1
    mock_db.query.side_effect = SQLAlchemyError("Connection failed")

    with pytest.raises(SQLAlchemyError):
        repository.get_book_by_id(book_id)

def test_get_book_by_id_unexpected_error(repository, mock_db):
    """Test get_book_by_id raises generic exceptions."""
    book_id = 1
    mock_db.query.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(RuntimeError):
        repository.get_book_by_id(book_id)


def test_update_book_success(repository, mock_db):
    """Test update_book successfully updates and returns a book."""
    from app.schemas.book import BookBase

    book_id = 1
    update_data = BookBase(title="Updated", author="Updated Author", published_year=2024, available=True)

    # Mock the existing book
    existing_book = MagicMock(spec=Book)
    existing_book.id = 1
    existing_book.title = "Old Title"
    existing_book.author = "Old Author"

    with patch.object(repository, 'get_book_by_id', return_value=existing_book):
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        result = repository.update_book(book_id, update_data)

    assert result == existing_book
    assert existing_book.title == "Updated"
    assert existing_book.author == "Updated Author"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_update_book_not_found(repository, mock_db):
    """Test update_book raises ValueError when book not found."""
    from app.schemas.book import BookBase

    book_id = 999
    update_data = BookBase(title="Updated", author="Author", published_year=2024, available=True)

    with patch.object(repository, 'get_book_by_id', side_effect=ValueError(f"Book with id {book_id} not found")):
        with pytest.raises(ValueError) as exc_info:
            repository.update_book(book_id, update_data)
        assert "not found" in str(exc_info.value)

def test_update_book_database_error(repository, mock_db):
    """Test update_book rolls back and re-raises SQLAlchemy error."""
    from app.schemas.book import BookBase

    book_id = 1
    update_data = BookBase(title="Updated", author="Author", published_year=2024, available=True)

    existing_book = MagicMock(spec=Book)
    mock_db.commit = MagicMock(side_effect=SQLAlchemyError("Constraint violation"))
    mock_db.rollback = MagicMock()

    with patch.object(repository, 'get_book_by_id', return_value=existing_book):
        with pytest.raises(SQLAlchemyError):
            repository.update_book(book_id, update_data)

    mock_db.rollback.assert_called_once()

def test_update_book_unexpected_error(repository, mock_db):
    """Test update_book rolls back and re-raises generic exceptions."""
    from app.schemas.book import BookBase

    book_id = 1
    update_data = BookBase(title="Updated", author="Author", published_year=2024, available=True)

    existing_book = MagicMock(spec=Book)
    mock_db.commit = MagicMock(side_effect=RuntimeError("Unexpected error"))
    mock_db.rollback = MagicMock()

    with patch.object(repository, 'get_book_by_id', return_value=existing_book):
        with pytest.raises(RuntimeError):
            repository.update_book(book_id, update_data)

    mock_db.rollback.assert_called_once()

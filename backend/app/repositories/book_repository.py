"""Book data access layer - pure data operations with no business logic."""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.book import Book
from app.schemas.book import BookBase
from app.common.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)


class BookRepository:
    """Repository for book data access operations.

    This layer handles all database interactions for books. It returns data
    as-is or None for missing records. Business logic validation and existence
    checks are performed in the service layer.
    """

    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db

    def get_all_books(self) -> list[Book]:
        """Retrieve all books from the database.

        Returns:
            list[Book]: List of all books (empty list if none exist).

        Raises:
            DatabaseError: If database query fails.
        """
        try:
            logger.info("Querying all books")
            books = self.db.query(Book).all()
            logger.info(f"Retrieved {len(books)} books")
            return books
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_books: {str(e)}")
            raise DatabaseError(f"Failed to retrieve books: {str(e)}")

    def create_book(self, book: BookBase) -> Book:
        """Create a new book in the database.

        Args:
            book: The book data to create.

        Returns:
            Book: The newly created book with auto-generated ID.

        Raises:
            DatabaseError: If database operation fails.
        """
        try:
            logger.info(f"Creating book: {book.title}")
            db_book = Book(**book.model_dump())
            self.db.add(db_book)
            self.db.commit()
            self.db.refresh(db_book)
            logger.info(f"Successfully created book: {db_book.id}")
            return db_book
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in create_book: {str(e)}")
            raise DatabaseError(f"Failed to create book: {str(e)}")

    def get_book_by_id(self, book_id: int) -> Book | None:
        """Retrieve a single book by ID.

        Args:
            book_id: The ID of the book to retrieve.

        Returns:
            Book: The book if found, None otherwise.

        Raises:
            DatabaseError: If database query fails.
        """
        try:
            logger.info(f"Querying book with id={book_id}")
            book = self.db.query(Book).filter(Book.id == book_id).first()
            if book:
                logger.info(f"Found book: {book.id}")
            else:
                logger.error(f"Book not found: {book_id}")
            return book
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_book_by_id: {str(e)}")
            raise DatabaseError(f"Failed to retrieve book: {str(e)}")

    def update_book(self, book_id: int, book_data: BookBase, db_book: Book) -> Book:
        """Update an existing book in the database.

        Args:
            book_id: The ID of the book to update (for logging).
            book_data: The new book data.
            db_book: The existing book object from the database.

        Returns:
            Book: The updated book.

        Raises:
            DatabaseError: If database operation fails.

        Note:
            The service layer is responsible for verifying the book exists before
            calling this method. This method assumes db_book is a valid object.
        """
        try:
            logger.info(f"Updating book: {book_id}")
            for key, value in book_data.model_dump(exclude_unset=True).items():
                setattr(db_book, key, value)
            self.db.commit()
            self.db.refresh(db_book)
            logger.info(f"Successfully updated book: {book_id}")
            return db_book
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in update_book: {str(e)}")
            raise DatabaseError(f"Failed to update book: {str(e)}")

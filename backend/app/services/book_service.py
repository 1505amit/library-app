from sqlalchemy.orm import Session
from app.repositories.book_repository import BookRepository
from app.common.exceptions import InvalidBookError, DatabaseError, BookNotFoundError
from app.schemas.book import BookBase
import logging

logger = logging.getLogger(__name__)


class BookService:
    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db
        self.books_repository = BookRepository(db)

    def get_all_books(self, page: int = 1, limit: int = 10) -> dict:
        """Fetch paginated books from the database.

        Retrieves a paginated list of book records with pagination metadata.

        Args:
            page (int): Page number (1-indexed). Defaults to 1.
            limit (int): Number of books per page. Defaults to 10.

        Returns:
            dict: Dictionary containing:
                - "data": List of Book objects for the current page
                - "pagination": Dictionary with pagination metadata (total, page, limit, pages)

        Raises:
            DatabaseError: If the database query fails due to connection or query issues.
        """
        logger.info(f"Retrieving books with page={page}, limit={limit}")
        # Calculate offset from page number
        offset = (page - 1) * limit
        # Get paginated books and total count
        books, total_count = self.books_repository.get_all_books(
            offset=offset, limit=limit)
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit
        # Validate page number
        if total_count > 0 and page > total_pages:
            logger.error(
                f"Invalid page number: {page} exceeds total pages: {total_pages}")
            raise InvalidBookError(
                f"Page {page} exceeds total pages {total_pages}")
        # Build response
        return {
            "data": books,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": total_pages
            }
        }

    def get_book_by_id(self, book_id: int):
        """Fetch a single book by its unique identifier.

        Retrieves a specific book record from the database using its ID.
        This is a business logic layer that verifies the book exists before returning it.

        Args:
            book_id (int): The unique identifier of the book to retrieve. Must be a positive integer.

        Returns:
            Book: The Book object with the specified ID.

        Raises:
            BookNotFoundError: If no book with the given ID exists in the database.
            DatabaseError: If the database query fails due to connection or query issues.
        """
        logger.info(f"Retrieving book with id {book_id}")
        book = self.books_repository.get_book_by_id(book_id)
        if not book:
            logger.error(f"Book not found with id {book_id}")
            raise BookNotFoundError(f"Book with id {book_id} not found")
        return book

    def create_book(self, book: BookBase):
        """Create a new book record with business logic validation.

        Validates the input data according to business rules, then persists the new book
        to the database. Input validation (format, length) is handled by Pydantic in the schema layer.

        Args:
            book (BookBase): A BookBase schema object containing the book details:
                - title: The book's title (1-255 characters, required)
                - author: The book's author (1-255 characters, required)
                - published_year: Year of publication (1000-2100, optional)
                - available: Whether the book is available (defaults to True)

        Returns:
            Book: The newly created Book object with an assigned ID.

        Raises:
            InvalidBookError: If business logic validation fails (e.g., published_year > 2026).
            DatabaseError: If the database operation fails due to connection or constraint issues.
        """
        logger.info(f"Creating new book: {book.title}")

        # Business logic validation
        self._validate_book_data(book)

        return self.books_repository.create_book(book)

    def update_book(self, book_id: int, book: BookBase):
        """Update an existing book record with business logic validation.

        Verifies the book exists, validates the input data according to business rules,
        then persists the changes to the database. Partial updates are supported - only
        provided fields are updated.

        Args:
            book_id (int): The unique identifier of the book to update. Must be a positive integer.
            book (BookBase): A BookBase schema object containing updated book details:
                - title: The book's new title (1-255 characters, required)
                - author: The book's new author (1-255 characters, required)
                - published_year: Updated publication year (1000-2100, optional)
                - available: Updated availability status (optional)

        Returns:
            Book: The updated Book object with all current values.

        Raises:
            BookNotFoundError: If no book with the given ID exists in the database.
            InvalidBookError: If business logic validation fails (e.g., published_year > 2026).
            DatabaseError: If the database operation fails due to connection or constraint issues.
        """
        logger.info(f"Updating book with id {book_id}")

        # Verify book exists (service responsibility: business logic)
        existing_book = self.books_repository.get_book_by_id(book_id)
        if not existing_book:
            logger.error(f"Book not found for update: {book_id}")
            raise BookNotFoundError(f"Book with id {book_id} not found")

        # Business logic validation
        self._validate_book_data(book)

        # Update (repository only handles data persistence)
        return self.books_repository.update_book(book_id, book, existing_book)

    def _validate_book_data(self, book: BookBase) -> None:
        """Validate book data against business rules.

        Performs domain-specific validation that cannot be handled at the schema (Pydantic) level.
        Schema-level validation (format, length, type) is already handled by Pydantic.
        This method checks business logic constraints.

        Current validations:
        - published_year must not be in the future (> 2026)

        Args:
            book (BookBase): The book data to validate.

        Raises:
            InvalidBookError: If any business rule validation fails with a descriptive message
                about which rule was violated.

        Returns:
            None: Raises an exception if validation fails, returns None if validation passes.
        """
        # Validate published_year is not too far in the future
        if book.published_year:
            if book.published_year > 2026:
                raise InvalidBookError(
                    f"Published year cannot be in the future (provided: {book.published_year})"
                )

        logger.info(f"Book data validation passed for: {book.title}")

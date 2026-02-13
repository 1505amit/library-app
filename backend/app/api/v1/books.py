from app.services.book_service import BookService
from app.schemas.book import BookResponse, BookBase, PaginatedBookResponse
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.common.database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def get_book_service(db: Session = Depends(get_db)) -> BookService:
    """Create and return a BookService instance for dependency injection.

    This is a FastAPI dependency function that provides a BookService instance
    to endpoint handlers. The database session is obtained from the dependency
    injection system.

    Args:
        db (Session): SQLAlchemy database session injected by FastAPI's dependency system.

    Returns:
        BookService: An initialized BookService instance ready to handle business logic operations.
    """
    logger.info("Initializing BookService")
    return BookService(db)


@router.get("", response_model=PaginatedBookResponse)
def get_books(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(
        10, ge=1, le=100, description="Number of items per page"),
    service: BookService = Depends(get_book_service)
):
    """Fetch paginated books from the library.

    Retrieves a paginated list of all books available in the library database.
    Uses page and limit query parameters to control pagination.

    Args:
        page (int): Page number starting from 1. Defaults to 1. Must be >= 1.
        limit (int): Maximum number of books to return per page. Defaults to 10.
                    Must be between 1 and 100.
        service (BookService): BookService instance injected by FastAPI dependency system.

    Returns:
        PaginatedBookResponse: An object containing:
            - data: List of Book objects for the current page
            - pagination: Metadata including total, page, limit, and total pages

    Raises:
        DatabaseError: If the database query fails (handled by exception middleware and returns 500).
    """
    logger.info(f"Retrieving books with page={page}, limit={limit}")
    return service.get_all_books(page=page, limit=limit)


@router.post("", response_model=BookResponse)
def add_book(book: BookBase, service: BookService = Depends(get_book_service)):
    """Create a new book in the library.

    Accepts book details, validates them according to business rules, and persists
    the new book to the database. The newly created book is returned with its
    auto-generated ID.

    Args:
        book (BookBase): A BookBase schema containing the book's details:
            - title: Book title (1-255 characters, required)
            - author: Author name (1-255 characters, required)
            - published_year: Year of publication (1000-2100, optional)
            - available: Availability status (defaults to True)
        service (BookService): BookService instance injected by FastAPI dependency system.

    Returns:
        BookResponse: The newly created Book object with an assigned ID and all details.

    Raises:
        InvalidBookError: If business validation fails (e.g., published_year > 2026).
            Handled by exception middleware and returns 400.
        DatabaseError: If the database operation fails. Handled by exception middleware
            and returns 500.
    """
    logger.info(f"Creating new book: {book.title}")
    return service.create_book(book)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookBase, service: BookService = Depends(get_book_service)):
    """Update an existing book in the library.

    Verifies the book exists, validates the provided details according to business rules,
    then updates the book record in the database. Only provided fields are updated,
    supporting partial updates.

    Args:
        book_id (int): The unique identifier of the book to update. Must be a positive integer.
        book (BookBase): A BookBase schema containing updated book details:
            - title: Updated book title (1-255 characters, required)
            - author: Updated author name (1-255 characters, required)
            - published_year: Updated publication year (1000-2100, optional)
            - available: Updated availability status (optional)
        service (BookService): BookService instance injected by FastAPI dependency system.

    Returns:
        BookResponse: The updated Book object with all current values.

    Raises:
        BookNotFoundError: If no book with the given ID exists. Handled by exception
            middleware and returns 404.
        InvalidBookError: If business validation fails (e.g., published_year > 2026).
            Handled by exception middleware and returns 400.
        DatabaseError: If the database operation fails. Handled by exception middleware
            and returns 500.
    """
    logger.info(f"Updating book with id {book_id}")
    return service.update_book(book_id, book)

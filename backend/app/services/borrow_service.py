"""Borrow business logic service layer - orchestration and validation."""
from sqlalchemy.orm import Session
from app.repositories.borrow_repository import BorrowRepository
from app.repositories.book_repository import BookRepository
from app.repositories.member_repository import MemberRepository
from app.schemas.borrow import BorrowBase
from app.common.exceptions import (
    BorrowNotFoundError,
    InvalidBorrowError,
    BookNotFoundError,
    MemberNotFoundError,
)
import logging

logger = logging.getLogger(__name__)


class BorrowService:
    """Service layer for borrow operations.

    Handles business logic, validation, and orchestration. Uses multiple
    repositories for different entities. Throws typed business exceptions
    for specific error conditions.
    """

    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db
        self.borrow_repository = BorrowRepository(db)
        self.book_repository = BookRepository(db)
        self.member_repository = MemberRepository(db)

    def get_all_borrows(self, returned: bool = True, member_id: int = None, book_id: int = None, page: int = 1, limit: int = 10) -> dict:
        """Retrieve paginated borrow records with optional filtering.

        Args:
            returned: Include returned books if True, only active borrows if False.
            member_id: Filter by member ID if provided.
            book_id: Filter by book ID if provided.
            page (int): Page number (1-indexed). Defaults to 1.
            limit (int): Number of borrow records per page. Defaults to 10.

        Returns:
            dict: Dictionary containing:
                - "data": List of BorrowDetailedResponse objects for the current page
                - "pagination": Dictionary with pagination metadata (total, page, limit, pages)

        Raises:
            InvalidBorrowError: If page number exceeds total pages.
            DatabaseError: If database operation fails.
        """
        logger.info(
            f"Service: retrieving borrow records (returned={returned}, member={member_id}, book={book_id}, page={page}, limit={limit})")
        # Calculate offset from page number
        offset = (page - 1) * limit
        # Get paginated borrow records and total count
        borrow_records, total_count = self.borrow_repository.get_all_borrows(
            returned=returned,
            member_id=member_id,
            book_id=book_id,
            offset=offset,
            limit=limit
        )
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit
        # Validate page number
        if total_count > 0 and page > total_pages:
            logger.warning(
                f"Invalid page number: {page} exceeds total pages: {total_pages}")
            raise InvalidBorrowError(
                f"Page {page} exceeds total pages {total_pages}")
        # Build response
        return {
            "data": borrow_records,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": total_pages
            }
        }

    def borrow_book(self, borrow_data: BorrowBase):
        """Borrow a book for a member.

        Validates that:
        - Book exists and is available
        - Member exists and is active

        Then creates a borrow record and marks the book as unavailable.

        Args:
            borrow_data: The borrow data (book_id, member_id).

        Returns:
            BorrowRecord: The newly created borrow record.

        Raises:
            BookNotFoundError: If book does not exist.
            InvalidBorrowError: If book is not available or member issues.
            MemberNotFoundError: If member does not exist.
            DatabaseError: If database operation fails.
        """
        logger.info(
            f"Service: borrowing book {borrow_data.book_id} for member {borrow_data.member_id}")

        # Verify and get book using BookRepository
        book = self.book_repository.get_book_by_id(borrow_data.book_id)
        if not book:
            logger.error(f"Book not found: {borrow_data.book_id}")
            raise BookNotFoundError(
                f"Book with id {borrow_data.book_id} not found")

        if not book.available:
            logger.error(f"Book not available: {borrow_data.book_id}")
            raise InvalidBorrowError(
                f"Book with id {borrow_data.book_id} is not available")

        # Verify and get member using MemberRepository
        member = self.member_repository.get_member_by_id(borrow_data.member_id)
        if not member:
            logger.error(f"Member not found: {borrow_data.member_id}")
            raise MemberNotFoundError(
                f"Member with id {borrow_data.member_id} not found")

        if not member.active:
            logger.error(f"Member not active: {borrow_data.member_id}")
            raise InvalidBorrowError(
                f"Member with id {borrow_data.member_id} is not active")

        # Create borrow record (repository handles marking book unavailable)
        borrow = self.borrow_repository.create_borrow(borrow_data, book)
        logger.info(f"Borrow record created successfully: {borrow.id}")
        return borrow

    def return_borrow(self, borrow_id: int):
        """Return a borrowed book.

        Validates that:
        - Borrow record exists
        - Book has not already been returned

        Then marks the borrow as returned and the book as available.

        Args:
            borrow_id: The ID of the borrow record to return.

        Returns:
            BorrowRecord: The updated borrow record.

        Raises:
            BorrowNotFoundError: If borrow record does not exist.
            InvalidBorrowError: If book has already been returned.
            DatabaseError: If database operation fails.
        """
        logger.info(f"Service: returning borrow {borrow_id}")

        # Verify and get borrow record
        borrow_record = self.borrow_repository.get_borrow_by_id(borrow_id)
        if not borrow_record:
            logger.error(f"Borrow record not found: {borrow_id}")
            raise BorrowNotFoundError(
                f"Borrow record with id {borrow_id} not found")

        # Check if already returned
        if borrow_record.returned_at is not None:
            logger.error(f"Borrow already returned: {borrow_id}")
            raise InvalidBorrowError(
                f"Borrow record with id {borrow_id} has already been returned")

        # Get the book using BookRepository for updating availability
        book = self.book_repository.get_book_by_id(borrow_record.book_id)
        if not book:
            logger.error(f"Book not found for borrow: {borrow_record.book_id}")
            raise BookNotFoundError(
                f"Book with id {borrow_record.book_id} not found")

        # Return the borrow record (repository handles marking book available)
        returned_borrow = self.borrow_repository.return_borrow(
            borrow_record, book)
        logger.info(f"Borrow record returned successfully: {borrow_id}")
        return returned_borrow

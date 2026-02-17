"""Borrow data access layer - pure data operations with no business logic."""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.borrow import BorrowRecord
from app.models.book import Book
from app.schemas.borrow import BorrowBase
from app.common.exceptions import DatabaseError
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class BorrowRepository:
    """Repository for borrow data access operations.

    This layer handles all database interactions for borrow records. It returns
    data as-is or None for missing records. Business logic validation and
    existence checks are performed in the service layer.
    """

    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db

    def get_all_borrows(self, returned: bool = True, member_id: int = None, book_id: int = None, offset: int = 0, limit: int = 10) -> tuple[list[BorrowRecord], int]:
        """Retrieve paginated borrow records with optional filtering.

        Args:
            returned: Include returned books if True, only active borrows if False.
            member_id: Filter by member ID if provided.
            book_id: Filter by book ID if provided.
            offset (int): Number of records to skip. Defaults to 0.
            limit (int): Maximum number of records to return. Defaults to 10.

        Returns:
            tuple[list[BorrowRecord], int]: A tuple containing:
                - List of borrow records for the current page
                - Total count of borrow records matching the filters

        Raises:
            DatabaseError: If database query fails.
        """
        try:
            logger.info(
                f"Querying borrow records with offset={offset}, limit={limit}")
            query = self.db.query(BorrowRecord)

            # Filter out returned books if returned is False
            if not returned:
                query = query.filter(BorrowRecord.returned_at.is_(None))

            # Filter by member_id if provided
            if member_id is not None:
                query = query.filter(BorrowRecord.member_id == member_id)

            # Filter by book_id if provided
            if book_id is not None:
                query = query.filter(BorrowRecord.book_id == book_id)

            # Get total count of filtered results
            total_count = query.count()
            # Get paginated results sorted by borrowed_at in descending order
            borrow_records = query.order_by(
                BorrowRecord.borrowed_at.desc()).offset(offset).limit(limit).all()
            logger.info(
                f"Retrieved {len(borrow_records)} borrow records out of {total_count} total")
            return borrow_records, total_count
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_borrows: {str(e)}")
            raise DatabaseError(f"Failed to retrieve borrow records: {str(e)}")

    def get_borrow_by_id(self, borrow_id: int) -> BorrowRecord | None:
        """Retrieve a single borrow record by ID.

        Args:
            borrow_id: The ID of the borrow record to retrieve.

        Returns:
            BorrowRecord: The borrow record if found, None otherwise.

        Raises:
            DatabaseError: If database query fails.
        """
        try:
            logger.info(f"Querying borrow with id={borrow_id}")
            borrow = self.db.query(BorrowRecord).filter(
                BorrowRecord.id == borrow_id).first()
            if borrow:
                logger.info(f"Found borrow: {borrow.id}")
            else:
                logger.error(f"Borrow not found: {borrow_id}")
            return borrow
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_borrow_by_id: {str(e)}")
            raise DatabaseError(f"Failed to retrieve borrow record: {str(e)}")

    def create_borrow(self, borrow_data: BorrowBase, book: Book) -> BorrowRecord:
        """Create a new borrow record in the database.

        Args:
            borrow_data: The borrow data to create.
            book: The book object being borrowed (for updating availability).

        Returns:
            BorrowRecord: The newly created borrow record.

        Raises:
            DatabaseError: If database operation fails.

        Note:
            The service layer is responsible for verifying book exists, is available,
            member exists, and member is active before calling this method.
            This method assumes all entities are valid.
        """
        try:
            logger.info(
                f"Creating borrow for book={borrow_data.book_id}, member={borrow_data.member_id}")

            # Create borrow record
            db_borrow = BorrowRecord(**borrow_data.model_dump())
            self.db.add(db_borrow)

            # Mark book as unavailable
            book.available = False

            self.db.commit()
            self.db.refresh(db_borrow)
            logger.info(f"Successfully created borrow record: {db_borrow.id}")
            return db_borrow
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in create_borrow: {str(e)}")
            raise DatabaseError(f"Failed to create borrow record: {str(e)}")

    def return_borrow(self, borrow_record: BorrowRecord, book: Book) -> BorrowRecord:
        """Mark a borrow record as returned and restore book availability.

        Args:
            borrow_record: The borrow record to update.
            book: The book object being returned.

        Returns:
            BorrowRecord: The updated borrow record.

        Raises:
            DatabaseError: If database operation fails.

        Note:
            The service layer is responsible for verifying the borrow record exists
            and has not already been returned before calling this method.
        """
        try:
            logger.info(f"Returning borrow: {borrow_record.id}")

            # Update borrow record with return date
            borrow_record.returned_at = datetime.now(timezone.utc)

            # Mark book as available
            book.available = True

            self.db.commit()
            self.db.refresh(borrow_record)
            logger.info(
                f"Successfully returned borrow record: {borrow_record.id}")
            return borrow_record
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in return_borrow: {str(e)}")
            raise DatabaseError(f"Failed to return borrow record: {str(e)}")

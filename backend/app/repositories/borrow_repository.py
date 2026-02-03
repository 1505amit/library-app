from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.borrow import BorrowRecord
from app.models.book import Book
from app.models.member import Member
from app.schemas.borrow import BorrowBase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BorrowRepository:
    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db

    def create_borrow(self, borrow: BorrowBase):
        try:
            # Verify book exists and is available
            book = self.db.query(Book).filter(
                Book.id == borrow.book_id).first()
            if not book:
                raise ValueError(f"Book with id {borrow.book_id} not found")
            if not book.available:
                raise ValueError(
                    f"Book with id {borrow.book_id} is not available")

            # Verify member exists
            member = self.db.query(Member).filter(
                Member.id == borrow.member_id).first()
            if not member:
                raise ValueError(
                    f"Member with id {borrow.member_id} not found")
            if not member.active:
                raise ValueError(
                    f"Member with id {borrow.member_id} is not active")

            # Create borrow record
            db_borrow = BorrowRecord(**borrow.dict())
            self.db.add(db_borrow)

            # Mark book as unavailable
            book.available = False

            self.db.commit()
            self.db.refresh(db_borrow)
            return db_borrow
        except ValueError:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in create_borrow: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in create_borrow: {str(e)}")
            raise

    def get_all_borrows(self, include_returned: bool = True):
        try:
            query = self.db.query(BorrowRecord)

            # Filter out returned books if include_returned is False
            if not include_returned:
                query = query.filter(BorrowRecord.returned_at.is_(None))

            borrow_records = query.all()
            return borrow_records
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_borrows: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_all_borrows: {str(e)}")
            raise

    def return_borrow(self, borrow_id: int):
        try:
            # Fetch the borrow record
            borrow_record = self.db.query(BorrowRecord).filter(
                BorrowRecord.id == borrow_id).first()
            if not borrow_record:
                raise ValueError(
                    f"Borrow record with id {borrow_id} not found")

            # Check if already returned
            if borrow_record.returned_at is not None:
                raise ValueError(
                    f"Borrow record with id {borrow_id} has already been returned")

            # Fetch the book and mark it as available
            book = self.db.query(Book).filter(
                Book.id == borrow_record.book_id).first()
            if not book:
                raise ValueError(
                    f"Book with id {borrow_record.book_id} not found")

            # Update borrow record with return date
            borrow_record.returned_at = datetime.utcnow()
            # Mark book as available
            book.available = True

            self.db.commit()
            self.db.refresh(borrow_record)
            return borrow_record
        except ValueError:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in return_borrow: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in return_borrow: {str(e)}")
            raise

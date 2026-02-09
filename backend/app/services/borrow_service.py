from sqlalchemy.orm import Session
from app.repositories.borrow_repository import BorrowRepository
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.borrow import BorrowBase, BorrowReturnRequest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BorrowService:
    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db
        self.borrow_repository = BorrowRepository(db)

    def borrow_book(self, borrow: BorrowBase):
        try:
            return self.borrow_repository.create_borrow(borrow)
        except ValueError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error in borrow_book: {str(e)}")
            raise ValueError("Failed to borrow book from database")
        except Exception as e:
            logger.error(f"Unexpected error in borrow_book: {str(e)}")
            raise

    def get_all_borrows(self, returned: bool = True, member_id: int = None, book_id: int = None):
        try:
            return self.borrow_repository.get_all_borrows(
                returned=returned,
                member_id=member_id,
                book_id=book_id
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_borrows: {str(e)}")
            raise ValueError("Failed to retrieve borrow records from database")
        except Exception as e:
            logger.error(f"Unexpected error in get_all_borrows: {str(e)}")
            raise

    def return_borrow(self, borrow_id: int):
        try:
            return self.borrow_repository.return_borrow(borrow_id)
        except ValueError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error in return_borrow: {str(e)}")
            raise ValueError("Failed to return book to database")
        except Exception as e:
            logger.error(f"Unexpected error in return_borrow: {str(e)}")
            raise

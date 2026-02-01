from sqlalchemy.orm import Session
from app.repositories.book_repository import BookRepository
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class BookService:
    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db
        self.books_repository = BookRepository(db)

    def get_all_books(self):
        try:
            return self.books_repository.get_all_books()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_books: {str(e)}")
            raise ValueError("Failed to retrieve books from database")
        except Exception as e:
            logger.error(f"Unexpected error in get_all_books: {str(e)}")
            raise

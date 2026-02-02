from sqlalchemy.orm import Session
from app.repositories.book_repository import BookRepository
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.book import BookBase
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

    def create_book(self, book: BookBase):
        try:
            return self.books_repository.create_book(book)
        except SQLAlchemyError as e:
            logger.error(f"Database error in create_book: {str(e)}")
            raise ValueError("Failed to create book in database")
        except Exception as e:
            logger.error(f"Unexpected error in create_book: {str(e)}")
            raise

    def update_book(self, book_id: int, book: BookBase):
        try:
            return self.books_repository.update_book(book_id, book)
        except SQLAlchemyError as e:
            logger.error(f"Database error in update_book: {str(e)}")
            raise ValueError("Failed to update book in database")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in update_book: {str(e)}")
            raise

# repositories/book_repository.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.book import Book
from app.schemas.book import BookBase
import logging

logger = logging.getLogger(__name__)


class BookRepository:
    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db

    def get_all_books(self):
        try:
            books = self.db.query(Book).all()
            return books
        except SQLAlchemyError as e:
            logger.error(f"Database query failed in get_all_books: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_all_books: {str(e)}")
            raise

    def create_book(self, book: BookBase):
        try:
            db_book = Book(**book.dict())
            self.db.add(db_book)
            self.db.commit()
            self.db.refresh(db_book)
            return db_book
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in create_book: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in create_book: {str(e)}")
            raise

    def get_book_by_id(self, book_id: int):
        try:
            book = self.db.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise ValueError(f"Book with id {book_id} not found")
            return book
        except SQLAlchemyError as e:
            logger.error(f"Database query failed in get_book_by_id: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_book_by_id: {str(e)}")
            raise

    def update_book(self, book_id: int, book: BookBase):
        try:
            db_book = self.get_book_by_id(book_id)
            for key, value in book.dict().items():
                setattr(db_book, key, value)
            self.db.commit()
            self.db.refresh(db_book)
            return db_book
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in update_book: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in update_book: {str(e)}")
            raise

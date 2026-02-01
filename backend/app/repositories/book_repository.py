# repositories/book_repository.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.book import Book
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

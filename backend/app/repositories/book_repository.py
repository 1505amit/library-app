# repositories/book_repository.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.book import Book
from app.schemas.book import BookBase
from app.common.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)


class BookRepository:
    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db

    def get_all_books(self):
        """Fetch all books from the database.

        Executes a database query to retrieve all Book records currently stored.
        This is a pure data access operation with no business logic filtering.

        Returns:
            list[Book]: A list of all Book objects from the database, or an empty list if no books exist.

        Raises:
            DatabaseError: If the SQL query fails, database connection is lost, or any
                database-level exception occurs during the fetch operation.
        """
        try:
            logger.info("Fetching all books from database")
            books = self.db.query(Book).all()
            return books
        except SQLAlchemyError as e:
            logger.error(f"Database query failed in get_all_books: {str(e)}")
            raise DatabaseError("Failed to retrieve books from database")
        except Exception as e:
            logger.error(f"Unexpected error in get_all_books: {str(e)}")
            raise DatabaseError(
                "An unexpected error occurred while retrieving books")

    def create_book(self, book: BookBase):
        """Persist a new book record to the database.

        Creates a new Book object from the provided schema, adds it to the database session,
        commits the transaction, and returns the newly created book with its generated ID.
        All input validation should be completed before calling this method.

        Args:
            book (BookBase): A validated BookBase schema containing the book's details.
                Expected to be pre-validated by the service layer.

        Returns:
            Book: The newly persisted Book object with an auto-generated ID from the database.

        Raises:
            DatabaseError: If the insert operation fails, database constraints are violated,
                commit fails, or any other database-level exception occurs.
        """
        try:
            logger.info(f"Creating book: {book.title}")
            db_book = Book(**book.model_dump())
            self.db.add(db_book)
            self.db.commit()
            self.db.refresh(db_book)
            logger.info(f"Book created with id {db_book.id}")
            return db_book
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in create_book: {str(e)}")
            raise DatabaseError("Failed to create book in database")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in create_book: {str(e)}")
            raise DatabaseError(
                "An unexpected error occurred while creating book")

    def get_book_by_id(self, book_id: int):
        """Retrieve a single book from the database by its ID.

        Executes a database query to fetch a specific Book record using its unique identifier.
        This is a pure data access operation that returns the record if it exists, or None otherwise.
        No exception is raised for missing records - the caller is responsible for handling None.

        Args:
            book_id (int): The unique database identifier of the book to retrieve.
                Must be a positive integer.

        Returns:
            Book | None: The Book object if found, or None if no book with the given ID exists.

        Raises:
            DatabaseError: If the SQL query fails, database connection is lost, or any
                database-level exception occurs during the fetch operation.
        """
        try:
            logger.info(f"Fetching book with id {book_id}")
            return self.db.query(Book).filter(Book.id == book_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database query failed in get_book_by_id: {str(e)}")
            raise DatabaseError("Failed to retrieve book from database")
        except Exception as e:
            logger.error(f"Unexpected error in get_book_by_id: {str(e)}")
            raise DatabaseError(
                "An unexpected error occurred while retrieving book")

    def update_book(self, book_id: int, book_data: BookBase, db_book: Book):
        """Update an existing book record in the database.

        Applies changes from the provided BookBase schema to the given Book object,
        including support for partial updates (only provided fields are modified).
        The transaction is committed and the updated object is refreshed from the database.

        Important: This method assumes the book already exists (verified by the caller).
        The caller (service layer) must verify the book exists before calling this method.

        Args:
            book_id (int): The unique database identifier of the book being updated.
                Used only for logging purposes.
            book_data (BookBase): A validated BookBase schema containing the new book details.
                Only fields explicitly set in the request will be updated (partial updates).
            db_book (Book): The existing Book object from the database that should be modified.
                Must be attached to the current session.

        Returns:
            Book: The updated Book object with all current values refreshed from the database.

        Raises:
            DatabaseError: If the update operation fails, database constraints are violated,
                commit fails, or any other database-level exception occurs. Automatically
                rolls back the transaction on failure.
        """
        try:
            logger.info(f"Updating book with id {book_id}")
            # Only update fields that were explicitly set in the request
            update_data = book_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_book, key, value)
            self.db.commit()
            self.db.refresh(db_book)
            logger.info(f"Book updated with id {book_id}")
            return db_book
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in update_book: {str(e)}")
            raise DatabaseError("Failed to update book in database")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in update_book: {str(e)}")
            raise DatabaseError(
                "An unexpected error occurred while updating book")

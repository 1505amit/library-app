"""
Custom application exceptions for domain-specific error handling.
Separates business logic errors from infrastructure errors.
"""


class AppException(Exception):
    """Base exception for all application errors"""
    pass


class BookNotFoundError(AppException):
    """Raised when a book with the specified ID does not exist"""
    pass


class InvalidBookError(AppException):
    """Raised when book data is invalid or violates business rules"""
    pass


class DatabaseError(AppException):
    """Raised when a database operation fails"""
    pass


class MemberNotFoundError(AppException):
    """Raised when a member with the specified ID does not exist"""
    pass


class InvalidMemberError(AppException):
    """Raised when member data is invalid or violates business rules"""
    pass


class BorrowNotFoundError(AppException):
    """Raised when a borrow record does not exist"""
    pass


class InvalidBorrowError(AppException):
    """Raised when borrow operation violates business rules"""
    pass

"""Borrow API endpoints - HTTP routing layer."""
from app.services.borrow_service import BorrowService
from app.schemas.borrow import BorrowResponse, BorrowRequest, BorrowReturnRequest, BorrowDetailedResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.common.database import get_db
import logging
from typing import List, Optional

router = APIRouter()
logger = logging.getLogger(__name__)


def get_borrow_service(db: Session = Depends(get_db)) -> BorrowService:
    """Dependency injection function providing BorrowService instance.

    Args:
        db: Database session from dependency injection.

    Returns:
        BorrowService: Initialized borrow service instance.
    """
    return BorrowService(db)


@router.get("", response_model=List[BorrowDetailedResponse])
def get_all_borrows(
    returned: bool = True,
    member_id: Optional[int] = None,
    book_id: Optional[int] = None,
    service: BorrowService = Depends(get_borrow_service)
):
    """Get borrowed books with optional filtering.

    Retrieves borrow records with optional filtering by status, member, or book.

    Query Parameters:
    - **returned** (bool, default: True): Include returned books in the response.
      - If True: Returns all borrow records (active and returned)
      - If False: Returns only active borrow records (not yet returned)
    - **member_id** (int, optional): Filter borrow records by member ID
    - **book_id** (int, optional): Filter borrow records by book ID

    Returns:
        List[BorrowDetailedResponse]: List of borrow records with book and member details.

    Raises:
        HTTP 500: If database operation fails (handled by exception middleware).
    """
    logger.info(
        f"listing borrows (returned={returned}, member={member_id}, book={book_id})")
    return service.get_all_borrows(
        returned=returned,
        member_id=member_id,
        book_id=book_id
    )


@router.post("", response_model=BorrowResponse)
def borrow_book(borrow: BorrowRequest, service: BorrowService = Depends(get_borrow_service)):
    """Borrow a book for a member.

    Creates a new borrow record, marking the book as unavailable until returned.

    Args:
        borrow: Borrow data including:
          - **book_id**: ID of the book to borrow (must be positive)
          - **member_id**: ID of the member borrowing the book (must be positive)
        service: Borrow service injected from get_borrow_service().

    Returns:
        BorrowResponse: The newly created borrow record.

    Raises:
        HTTP 404: If book or member does not exist (handled by exception middleware).
        HTTP 400: If book is unavailable or member is inactive (handled by exception middleware).
        HTTP 500: If database operation fails (handled by exception middleware).
    """
    logger.info(
        f"borrowing book {borrow.book_id} for member {borrow.member_id}")
    return service.borrow_book(borrow)


@router.patch("/{borrow_id}/return", response_model=BorrowDetailedResponse)
def return_book(borrow_id: int, service: BorrowService = Depends(get_borrow_service)):
    """Return a borrowed book.

    Marks a borrow record as returned and makes the book available again.
    The returned_at timestamp is automatically set to the current time.

    Args:
        borrow_id: ID of the borrow record to mark as returned (must be positive).
        service: Borrow service injected from get_borrow_service().

    Returns:
        BorrowDetailedResponse: The returned borrow record with book and member details.

    Raises:
        HTTP 404: If borrow record does not exist (handled by exception middleware).
        HTTP 400: If borrow has already been returned (handled by exception middleware).
        HTTP 500: If database operation fails (handled by exception middleware).
    """
    logger.info(f"returning borrow {borrow_id}")
    return service.return_borrow(borrow_id)

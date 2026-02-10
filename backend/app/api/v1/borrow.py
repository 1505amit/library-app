from app.services.borrow_service import BorrowService
from app.schemas.borrow import BorrowResponse, BorrowRequest, BorrowReturnRequest, BorrowDetailedResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.common.database import get_db
from datetime import datetime
import logging
from typing import List, Optional

router = APIRouter()
logger = logging.getLogger(__name__)


def get_borrow_service(db: Session = Depends(get_db)) -> BorrowService:
    try:
        return BorrowService(db)
    except Exception as e:
        logger.error(f"Failed to initialize BorrowService: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize borrow service"
        )


@router.get("", response_model=List[BorrowDetailedResponse])
def get_all_borrows(
    returned: bool = True,
    member_id: Optional[int] = None,
    book_id: Optional[int] = None,
    service: BorrowService = Depends(get_borrow_service)
):
    """
    Get borrowed books with optional filtering.

    Query Parameters:
    - **returned** (bool, default: True): Include returned books in the response.
      - If True: Returns all borrow records (active and returned)
      - If False: Returns only active borrow records (not yet returned)
    - **member_id** (int, optional): Filter borrow records by member ID
    - **book_id** (int, optional): Filter borrow records by book ID

    Returns a list of borrow records with their book and member details.
    """
    try:
        return service.get_all_borrows(
            returned=returned,
            member_id=member_id,
            book_id=book_id
        )
    except ValueError as e:
        logger.warning(f"Validation error retrieving borrow records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving borrow records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve borrow records"
        )


@router.post("", response_model=BorrowResponse)
def borrow_book(borrow: BorrowRequest, service: BorrowService = Depends(get_borrow_service)):
    """
    Borrow a book for a member.

    - **book_id**: ID of the book to borrow
    - **member_id**: ID of the member borrowing the book
    """
    try:
        return service.borrow_book(borrow)
    except ValueError as e:
        logger.warning(f"Validation error borrowing book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error borrowing book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to borrow book"
        )


@router.patch("/{borrow_id}/return", response_model=BorrowDetailedResponse)
def return_book(borrow_id: int, service: BorrowService = Depends(get_borrow_service)):
    """
    Return a borrowed book.

    The returned_at timestamp is automatically set to the current time by the backend.

    Path Parameters:
    - **borrow_id**: ID of the borrow record to mark as returned
    """
    try:
        return service.return_borrow(borrow_id)
    except ValueError as e:
        logger.warning(f"Validation error returning book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error returning book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to return book"
        )

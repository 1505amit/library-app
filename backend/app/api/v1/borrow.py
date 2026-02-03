from app.services.borrow_service import BorrowService
from app.schemas.borrow import BorrowResponse, BorrowRequest, BorrowReturnRequest
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.common.database import get_db
from datetime import datetime
import logging

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


@router.post("/", response_model=BorrowResponse)
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

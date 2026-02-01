from app.services.book_service import BookService
from app.schemas.book import BookResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.common.database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    try:
        return BookService(db)
    except Exception as e:
        logger.error(f"Failed to initialize BookService: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize book service"
        )


@router.get("/", response_model=list[BookResponse])
def list_books(service: BookService = Depends(get_book_service)):
    try:
        return service.get_all_books()
    except ValueError as e:
        logger.warning(f"Validation error getting books: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching books: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch books"
        )

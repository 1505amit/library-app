from app.services.book_service import BookService
from app.schemas.book import BookResponse, BookBase
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
def get_books(service: BookService = Depends(get_book_service)):
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
    
@router.post("/", response_model=BookResponse)
def add_book(book: BookBase, service: BookService = Depends(get_book_service)):
    try:
        return service.create_book(book)
    except ValueError as e:
        logger.warning(f"Validation error creating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create book"
        )
    
@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookBase, service: BookService = Depends(get_book_service)):
    try:
        return service.update_book(book_id, book)
    except ValueError as e:
        logger.warning(f"Validation error updating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update book"
        )

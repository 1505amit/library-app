from app.services.member_service import MemberService
from app.api.v1.books import get_book_service
from app.common.database import get_db
from app.schemas.member import MemberBase, MemberResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    try:
        return MemberService(db)
    except Exception as e:
        logger.error(f"Failed to initialize MemberService: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize member service"
        )


@router.post("/", response_model=MemberResponse)
def add_member(member: MemberBase, service: MemberService = Depends(get_member_service)):
    try:
        member = service.create_member(member)
        return member
    except ValueError as e:
        logger.warning(f"Validation error creating member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create member"
        )

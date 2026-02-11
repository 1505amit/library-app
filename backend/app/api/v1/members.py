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


@router.post("", response_model=MemberResponse)
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


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member: MemberBase, service: MemberService = Depends(get_member_service)):
    try:
        updated_member = service.update_member(member_id, member)
        return updated_member
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            logger.warning(f"Member not found: {member_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        logger.warning(f"Validation error updating member: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        logger.error(f"Error updating member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update member"
        )


@router.get("", response_model=list[MemberResponse])
def list_members(service: MemberService = Depends(get_member_service)):
    try:
        members = service.get_all_members()
        return members
    except ValueError as e:
        logger.warning(f"Validation error retrieving members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve members"
        )

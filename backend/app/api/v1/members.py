"""Member API endpoints - HTTP routing layer."""
from app.services.member_service import MemberService
from app.common.database import get_db
from app.schemas.member import MemberBase, MemberResponse, PaginatedMemberResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    """Dependency injection function providing MemberService instance.

    Args:
        db: Database session from dependency injection.

    Returns:
        MemberService: Initialized member service instance.
    """
    return MemberService(db)


@router.get("", response_model=PaginatedMemberResponse)
def list_members(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(
        10, ge=1, le=100, description="Number of items per page"),
    service: MemberService = Depends(get_member_service)
):
    """Get paginated members.

    Retrieves a paginated list of all members in the system.
    Uses page and limit query parameters to control pagination.

    Args:
        page (int): Page number starting from 1. Defaults to 1. Must be >= 1.
        limit (int): Maximum number of members to return per page. Defaults to 10.
                    Must be between 1 and 100.
        service: Member service injected from get_member_service().

    Returns:
        PaginatedMemberResponse: An object containing:
            - data: List of Member objects for the current page
            - pagination: Metadata including total, page, limit, and total pages

    Raises:
        HTTP 400: If page number is invalid (handled by exception middleware).
        HTTP 500: If database operation fails (handled by exception middleware).
    """
    logger.info(f"listing members with page={page}, limit={limit}")
    return service.get_all_members(page=page, limit=limit)


@router.post("", response_model=MemberResponse)
def add_member(member: MemberBase, service: MemberService = Depends(get_member_service)):
    """Create a new member.

    Creates a new member with the provided data. Email must be unique.

    Args:
        member: Member data for creation (validated by Pydantic).
        service: Member service injected from get_member_service().

    Returns:
        MemberResponse: The newly created member with auto-generated ID.

    Raises:
        HTTP 400: If member data is invalid or violates business rules (handled by exception middleware).
        HTTP 409: If email already exists (handled by exception middleware).
        HTTP 500: If database operation fails (handled by exception middleware).
    """
    logger.info(f"creating member with email={member.email}")
    return service.create_member(member)


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member: MemberBase, service: MemberService = Depends(get_member_service)):
    """Update an existing member.

    Updates a member's information. Email must remain unique.

    Args:
        member_id: The ID of the member to update.
        member: Updated member data (validated by Pydantic).
        service: Member service injected from get_member_service().

    Returns:
        MemberResponse: The updated member.

    Raises:
        HTTP 404: If member does not exist (handled by exception middleware).
        HTTP 400: If member data is invalid or violates business rules (handled by exception middleware).
        HTTP 409: If email already exists (handled by exception middleware).
        HTTP 500: If database operation fails (handled by exception middleware).
    """
    logger.info(f"updating member {member_id}")
    return service.update_member(member_id, member)

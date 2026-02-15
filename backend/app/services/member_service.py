"""Member business logic service layer - orchestration and validation."""
from app.repositories.member_repository import MemberRepository
from app.schemas.member import MemberBase
from app.common.exceptions import MemberNotFoundError, InvalidMemberError
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class MemberService:
    """Service layer for member operations.

    Handles business logic, validation, and orchestration. Throws typed
    business exceptions for specific error conditions.
    """

    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db
        self.member_repository = MemberRepository(db)

    def get_all_members(self, page: int = 1, limit: int = 10) -> dict:
        """Retrieve paginated members.

        Retrieves a paginated list of member records with pagination metadata.

        Args:
            page (int): Page number (1-indexed). Defaults to 1.
            limit (int): Number of members per page. Defaults to 10.

        Returns:
            dict: Dictionary containing:
                - "data": List of Member objects for the current page
                - "pagination": Dictionary with pagination metadata (total, page, limit, pages)

        Raises:
            DatabaseError: If the database query fails due to connection or query issues.
            InvalidMemberError: If page number exceeds total pages.
        """
        logger.info(
            f"Service: retrieving members with page={page}, limit={limit}")
        # Calculate offset from page number
        offset = (page - 1) * limit
        # Get paginated members and total count
        members, total_count = self.member_repository.get_all_members(
            offset=offset, limit=limit)
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit
        # Validate page number
        if total_count > 0 and page > total_pages:
            logger.error(
                f"Invalid page number: {page} exceeds total pages: {total_pages}")
            raise InvalidMemberError(
                f"Page {page} exceeds total pages {total_pages}")
        # Build response
        return {
            "data": members,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": total_pages
            }
        }

    def get_member_by_id(self, member_id: int):
        """Retrieve a single member by ID.

        Args:
            member_id: The ID of the member to retrieve.

        Returns:
            Member: The member if found.

        Raises:
            MemberNotFoundError: If member does not exist.
            DatabaseError: If database operation fails.
        """
        logger.info(f"Service: retrieving member {member_id}")
        member = self.member_repository.get_member_by_id(member_id)

        if not member:
            logger.error(f"Member not found: {member_id}")
            raise MemberNotFoundError(
                f"Member with id {member_id} not found")

        return member

    def create_member(self, member_data: MemberBase):
        """Create a new member.

        Args:
            member_data: The member data to create.

        Returns:
            Member: The newly created member.

        Raises:
            InvalidMemberError: If member data violates business rules.
            DatabaseError: If database operation fails.
        """
        logger.info(
            f"Service: creating member with email={member_data.email}")

        # Create in repository
        member = self.member_repository.create_member(member_data)
        logger.info(f"Member created successfully: {member.id}")
        return member

    def update_member(self, member_id: int, member_data: MemberBase):
        """Update an existing member.

        Args:
            member_id: The ID of the member to update.
            member_data: The new member data.

        Returns:
            Member: The updated member.

        Raises:
            MemberNotFoundError: If member does not exist.
            InvalidMemberError: If member data violates business rules.
            DatabaseError: If database operation fails.
        """
        logger.info(f"Service: updating member {member_id}")

        # Check if member exists
        db_member = self.member_repository.get_member_by_id(member_id)
        if not db_member:
            logger.error(f"Member not found for update: {member_id}")
            raise MemberNotFoundError(
                f"Member with id {member_id} not found")

        # Update in repository
        member = self.member_repository.update_member(
            member_id, member_data, db_member)
        logger.info(f"Member updated successfully: {member_id}")
        return member

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

    def get_all_members(self) -> list:
        """Retrieve all members.

        Returns:
            list: List of all members (empty if none exist).

        Raises:
            DatabaseError: If database operation fails.
        """
        logger.info("Service: retrieving all members")
        return self.member_repository.get_all_members()

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

        Validates that the member data meets business requirements before creation.

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

        # Validate member data
        self._validate_member_data(member_data)

        # Create in repository
        member = self.member_repository.create_member(member_data)
        logger.info(f"Member created successfully: {member.id}")
        return member

    def update_member(self, member_id: int, member_data: MemberBase):
        """Update an existing member.

        Validates that member exists and data meets business requirements before update.

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

        # Validate member data
        self._validate_member_data(member_data)

        # Update in repository
        member = self.member_repository.update_member(
            member_id, member_data, db_member)
        logger.info(f"Member updated successfully: {member_id}")
        return member

    def _validate_member_data(self, member_data: MemberBase) -> None:
        """Validate member data against business rules.

        Args:
            member_data: The member data to validate.

        Raises:
            InvalidMemberError: If member data violates business rules.
        """
        # Email format validation (already done by Pydantic in schema)
        # Additional business rules can be added here as needed
        if not member_data.name or not member_data.name.strip():
            raise InvalidMemberError("Member name cannot be empty")

        if not member_data.email or not member_data.email.strip():
            raise InvalidMemberError("Member email cannot be empty")

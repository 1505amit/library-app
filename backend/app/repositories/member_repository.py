"""Member data access layer - pure data operations with no business logic."""
from app.models import Member
from app.schemas.member import MemberBase
from app.common.exceptions import DatabaseError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

logger = logging.getLogger(__name__)


class MemberRepository:
    """Repository for member data access operations.

    This layer handles all database interactions for members. It returns data
    as-is or None for missing records. Business logic validation and existence
    checks are performed in the service layer.
    """

    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db

    def get_all_members(self) -> list[Member]:
        """Retrieve all members from the database.

        Returns:
            list[Member]: List of all members (empty list if none exist).

        Raises:
            DatabaseError: If database query fails.
        """
        try:
            logger.info("Querying all members")
            members = self.db.query(Member).all()
            logger.info(f"Retrieved {len(members)} members")
            return members
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_members: {str(e)}")
            raise DatabaseError(f"Failed to retrieve members: {str(e)}")

    def get_member_by_id(self, member_id: int) -> Member | None:
        """Retrieve a single member by ID.

        Args:
            member_id: The ID of the member to retrieve.

        Returns:
            Member: The member if found, None otherwise.

        Raises:
            DatabaseError: If database query fails.
        """
        try:
            logger.info(f"Querying member with id={member_id}")
            member = self.db.query(Member).filter(
                Member.id == member_id).first()
            if member:
                logger.info(f"Found member: {member.id}")
            else:
                logger.info(f"Member not found: {member_id}")
            return member
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_member_by_id: {str(e)}")
            raise DatabaseError(f"Failed to retrieve member: {str(e)}")

    def create_member(self, member_data: MemberBase) -> Member:
        """Create a new member in the database.

        Args:
            member_data: The member data to create.

        Returns:
            Member: The newly created member with auto-generated ID.

        Raises:
            DatabaseError: If database operation fails (including constraint violations).
        """
        try:
            logger.info(f"Creating member with email={member_data.email}")
            db_member = Member(**member_data.dict())
            self.db.add(db_member)
            self.db.commit()
            self.db.refresh(db_member)
            logger.info(f"Successfully created member: {db_member.id}")
            return db_member
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error in create_member: {str(e)}")
            if "email" in str(e).lower():
                raise DatabaseError(
                    f"Email already exists: {member_data.email}")
            raise DatabaseError(
                f"Member creation failed due to constraint violation: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in create_member: {str(e)}")
            raise DatabaseError(f"Failed to create member: {str(e)}")

    def update_member(self, member_id: int, member_data: MemberBase, db_member: Member) -> Member:
        """Update an existing member in the database.

        Args:
            member_id: The ID of the member to update (for logging).
            member_data: The new member data.
            db_member: The existing member object from the database.

        Returns:
            Member: The updated member.

        Raises:
            DatabaseError: If database operation fails (including constraint violations).

        Note:
            The service layer is responsible for verifying the member exists before
            calling this method. This method assumes db_member is a valid object.
        """
        try:
            logger.info(f"Updating member: {member_id}")
            for key, value in member_data.dict(exclude_unset=True).items():
                setattr(db_member, key, value)

            self.db.commit()
            self.db.refresh(db_member)
            logger.info(f"Successfully updated member: {member_id}")
            return db_member
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error in update_member: {str(e)}")
            if "email" in str(e).lower():
                raise DatabaseError(
                    f"Email already exists: {member_data.email}")
            raise DatabaseError(
                f"Member update failed due to constraint violation: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in update_member: {str(e)}")
            raise DatabaseError(f"Failed to update member: {str(e)}")

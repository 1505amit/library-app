from app.repositories.member_repository import MemberRepository
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.member import MemberBase
import logging

logger = logging.getLogger(__name__)


class MemberService:
    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db
        self.member_repository = MemberRepository(db)

    def create_member(self, member: MemberBase):
        try:
            return self.member_repository.create_member(member)
        except ValueError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error in create_member: {str(e)}")
            raise ValueError("Failed to create member in database")
        except Exception as e:
            logger.error(f"Unexpected error in create_member: {str(e)}")
            raise

from app.schemas.member import MemberResponse, MemberBase
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from app.models import Member

logger = logging.getLogger(__name__)


class MemberRepository:
    def __init__(self, db: Session):
        if not db:
            raise ValueError("Database session cannot be None")
        self.db = db

    def create_member(self, member: MemberBase):
        try:
            db_member = Member(**member.dict())
            self.db.add(db_member)
            self.db.commit()
            self.db.refresh(db_member)
            return db_member
        except IntegrityError as e:
            self.db.rollback()
            if "email" in str(e).lower():
                logger.warning(
                    f"Duplicate email in create_member: {member.email}")
                raise ValueError(f"Email {member.email} already exists")
            logger.error(f"Integrity error in create_member: {str(e)}")
            raise ValueError(
                "Failed to create member due to constraint violation")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in create_member: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in create_member: {str(e)}")
            raise

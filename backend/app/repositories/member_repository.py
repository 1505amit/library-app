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

    def update_member(self, member_id: int, member: MemberBase):
        try:
            db_member = self.db.query(Member).filter(
                Member.id == member_id).first()
            if not db_member:
                raise ValueError(f"Member with id {member_id} not found")

            for key, value in member.dict(exclude_unset=True).items():
                setattr(db_member, key, value)

            self.db.commit()
            self.db.refresh(db_member)
            return db_member
        except ValueError:
            raise
        except IntegrityError as e:
            self.db.rollback()
            if "email" in str(e).lower():
                logger.warning(
                    f"Duplicate email in update_member: {member.email}")
                raise ValueError(f"Email {member.email} already exists")
            logger.error(f"Integrity error in update_member: {str(e)}")
            raise ValueError(
                "Failed to update member due to constraint violation")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in update_member: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in update_member: {str(e)}")
            raise

    def get_all_members(self):
        try:
            members = self.db.query(Member).all()
            return members
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_members: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_all_members: {str(e)}")
            raise

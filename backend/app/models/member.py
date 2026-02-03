from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.database import Base


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(default=None)
    active: Mapped[bool] = mapped_column(default=True)

    borrow_records: Mapped[list["BorrowRecord"]] = relationship(
        back_populates="member", cascade="all, delete-orphan")

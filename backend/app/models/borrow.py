from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.common.database import Base


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey(
        "books.id", ondelete="CASCADE"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey(
        "members.id", ondelete="CASCADE"), index=True)
    borrowed_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False)
    returned_at: Mapped[datetime | None] = mapped_column(
        default=None, nullable=True)

    book: Mapped["Book"] = relationship(back_populates="borrow_records")
    member: Mapped["Member"] = relationship(back_populates="borrow_records")

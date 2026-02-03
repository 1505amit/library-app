from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, index=True)
    author: Mapped[str] = mapped_column(nullable=False, index=True)
    published_year: Mapped[int | None] = mapped_column(default=None)
    available: Mapped[bool] = mapped_column(default=True)

    borrow_records: Mapped[list["BorrowRecord"]] = relationship(
        back_populates="book", cascade="all, delete-orphan")

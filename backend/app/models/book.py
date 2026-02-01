from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.common.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str]
    author: Mapped[str]
    published_year: Mapped[int | None] = mapped_column(default=None)
    available: Mapped[bool] = mapped_column(default=True)

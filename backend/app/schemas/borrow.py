from pydantic import BaseModel, Field
from datetime import datetime


class BorrowBase(BaseModel):
    """Base schema for borrow operations with validation."""
    book_id: int = Field(..., gt=0, description="ID of the book to borrow")
    member_id: int = Field(..., gt=0,
                           description="ID of the member borrowing the book")


class BorrowRequest(BorrowBase):
    """Request schema for borrowing a book."""
    pass


class BorrowResponse(BorrowBase):
    """Response schema for borrow records."""
    id: int
    borrowed_at: datetime
    returned_at: datetime | None = None

    class Config:
        from_attributes = True


class BookInfo(BaseModel):
    """Book information for detailed borrow response."""
    id: int
    title: str
    author: str
    published_year: int | None = None

    class Config:
        from_attributes = True


class MemberInfo(BaseModel):
    """Member information for detailed borrow response."""
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class BorrowDetailedResponse(BorrowBase):
    """Detailed borrow response including book and member information."""
    id: int
    borrowed_at: datetime
    returned_at: datetime | None = None
    book: BookInfo
    member: MemberInfo

    class Config:
        from_attributes = True


class BorrowReturnRequest(BaseModel):
    """Request schema for returning a borrowed book."""
    returned_at: datetime = None

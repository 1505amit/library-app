from pydantic import BaseModel
from datetime import datetime


class BorrowBase(BaseModel):
    book_id: int
    member_id: int


class BorrowRequest(BorrowBase):
    pass


class BorrowResponse(BorrowBase):
    id: int
    borrowed_at: datetime
    returned_at: datetime | None = None

    class Config:
        from_attributes = True


class BorrowReturnRequest(BaseModel):
    returned_at: datetime = None

from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    author: str
    published_year: int | None = None
    available: bool = True

class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True

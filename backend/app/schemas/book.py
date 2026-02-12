from pydantic import BaseModel, Field, field_validator


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255,
                       description="Book title")
    author: str = Field(..., min_length=1, max_length=255,
                        description="Author name")
    published_year: int | None = Field(
        None, ge=1000, le=2100, description="Year of publication")
    available: bool = Field(
        True, description="Whether the book is available for borrowing")

    @field_validator('title', 'author', mode='after')
    @classmethod
    def normalize_text(cls, v):
        """Normalize: trim whitespace"""
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        str_strip_whitespace = True


class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True

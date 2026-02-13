from pydantic import BaseModel, Field, field_validator


class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


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


class PaginatedBookResponse(BaseModel):
    """Paginated response containing books and pagination metadata."""
    data: list[BookResponse] = Field(..., description="List of books")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")

from pydantic import BaseModel, field_validator


class MemberBase(BaseModel):
    """Base schema for member data with validation and normalization."""
    name: str
    email: str
    phone: str | None = None
    active: bool = True

    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Normalize member name: trim whitespace."""
        if not v or not v.strip():
            raise ValueError('name cannot be empty or whitespace only')
        return v.strip()

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email: trim whitespace and convert to lowercase."""
        if not v or not v.strip():
            raise ValueError('email cannot be empty or whitespace only')
        email = v.strip().lower()
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError('email must be a valid email format')
        return email

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: str | None) -> str | None:
        """Normalize phone: trim whitespace if provided."""
        if v is None:
            return None
        if isinstance(v, str):
            phone = v.strip()
            return phone if phone else None
        return v


class MemberResponse(MemberBase):
    """Schema for member responses including ID."""
    id: int

    class Config:
        from_attributes = True

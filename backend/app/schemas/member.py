from pydantic import BaseModel, Field, field_validator
import re


class MemberBase(BaseModel):
    """Base schema for member data with validation and normalization."""
    name: str = Field(..., min_length=1, max_length=255,
                      description="Member full name")
    email: str = Field(..., min_length=1, max_length=255,
                       description="Member email address")
    phone: str | None = Field(None, max_length=20,
                              description="Member phone number (10-20 alphanumeric characters with separators)")
    active: bool = Field(True, description="Whether the member is active")

    @field_validator('name', mode='after')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Normalize: trim whitespace."""
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator('email', mode='after')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email: RFC 5322 simplified pattern."""
        if isinstance(v, str):
            email = v.strip().lower()
            # More comprehensive email validation pattern
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise ValueError(
                    'email must be a valid email format (e.g., user@example.com)')
            return email
        return v

    @field_validator('phone', mode='after')
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Validate and normalize phone: must contain at least one digit and valid separators."""
        if v is None or (isinstance(v, str) and not v.strip()):
            return None

        if isinstance(v, str):
            phone = v.strip()

            # Check length
            if len(phone) < 10:
                raise ValueError('phone number must be at least 10 characters')

            # Check for at least one digit
            if not re.search(r'\d', phone):
                raise ValueError(
                    'phone number must contain at least one digit')

            # Check for valid characters (digits, spaces, dashes, parentheses, plus)
            if not re.match(r'^[\d\s\-\+\(\)\.]{10,20}$', phone):
                raise ValueError(
                    'phone number contains invalid characters (only digits, spaces, -, +, (, ), . allowed)')

            return phone
        return v

    class Config:
        str_strip_whitespace = True


class MemberResponse(MemberBase):
    """Schema for member responses including ID."""
    id: int

    class Config:
        from_attributes = True

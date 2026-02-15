"""Unit tests for MemberBase field validators in member schema.

Tests cover the field validators in MemberBase:
- normalize_name: @field_validator('name', mode='after') - strips whitespace
- validate_email: @field_validator('email', mode='after') - validates format, strips, lowercases
- validate_phone: @field_validator('phone', mode='after') - validates phone, handles None, strips
- Field constraints: min_length, max_length, default values
- Config: str_strip_whitespace = True
"""
import pytest
from pydantic import ValidationError

from app.schemas.member import MemberBase


# ============================================================================
# normalize_name Validator Tests
# ============================================================================

class TestNormalizeNameValidator:
    """Tests for @field_validator('name') - normalize_name function"""

    def test_normalizes_name_whitespace(self):
        """Test normalize_name strips leading/trailing whitespace and preserves internal spaces."""
        m1 = MemberBase(name="  John  ", email="j@e.com")
        assert m1.name == "John"

        m2 = MemberBase(name="  John Doe  ", email="j@e.com")
        assert m2.name == "John Doe"

        m3 = MemberBase(name="John  Doe", email="j@e.com")
        assert m3.name == "John  Doe"


# ============================================================================
# validate_email Validator Tests
# ============================================================================

class TestValidateEmailValidator:
    """Tests for @field_validator('email') - validate_email function"""

    def test_normalizes_email_whitespace_and_case(self):
        """Test validate_email strips, lowercases, and accepts various formats."""
        m1 = MemberBase(name="John", email="  JOHN@EXAMPLE.COM  ")
        assert m1.email == "john@example.com"

        # Test various valid email patterns
        valid_emails = [
            "user@example.com",
            "john.doe@example.com",
            "john+tag@example.com",
            "john_name@example.com",
            "a@example.co.uk",
        ]
        for email in valid_emails:
            m = MemberBase(name="John", email=email)
            assert m.email == email.lower()

    def test_rejects_invalid_email_format(self):
        """Test validate_email rejects invalid formats."""
        invalid_emails = [
            "johnexample.com",  # missing @
            "@example.com",     # missing local part
            "john@",            # missing domain
            "john@example",     # missing TLD
            "john@example.c",   # single letter TLD
            "john..doe@example.com",  # consecutive dots
            "john doe@example.com",   # spaces
        ]
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                MemberBase(name="John", email=email)


# ============================================================================
# validate_phone Validator Tests
# ============================================================================

class TestValidatePhoneValidator:
    """Tests for @field_validator('phone') - validate_phone function"""

    def test_phone_none_and_empty_handling(self):
        """Test validate_phone handles None, empty string, and whitespace-only as None."""
        m1 = MemberBase(name="John", email="j@e.com", phone=None)
        assert m1.phone is None

        m2 = MemberBase(name="John", email="j@e.com", phone="")
        assert m2.phone is None

        m3 = MemberBase(name="John", email="j@e.com", phone="   ")
        assert m3.phone is None

    def test_normalizes_phone_whitespace(self):
        """Test validate_phone strips leading/trailing whitespace."""
        m = MemberBase(name="John", email="j@e.com", phone="  123-456-7890  ")
        assert m.phone == "123-456-7890"

    def test_accepts_valid_phone_formats(self):
        """Test validate_phone accepts various valid formats."""
        valid_phones = [
            "1234567890",           # digits only
            "123 456 7890",         # with spaces
            "123-456-7890",         # with dashes
            "(123) 456-7890",       # with parentheses
            "+1-234-567-8900",      # international with plus
            "123.456.7890",         # with dots
        ]
        for phone in valid_phones:
            m = MemberBase(name="John", email="j@e.com", phone=phone)
            assert m.phone == phone

    def test_rejects_invalid_phone_format(self):
        """Test validate_phone rejects invalid formats."""
        invalid_phones = [
            "123456789",            # less than 10 chars
            "abcd-efgh-ijkl",       # no digits
            "123-456-7890&ext",     # invalid characters
        ]
        for phone in invalid_phones:
            with pytest.raises(ValidationError):
                MemberBase(name="John", email="j@e.com", phone=phone)

    def test_phone_boundary_lengths(self):
        """Test validate_phone accepts boundary lengths (10 and 20 chars)."""
        m1 = MemberBase(name="John", email="j@e.com", phone="1234567890")
        assert m1.phone == "1234567890"

        m2 = MemberBase(name="John", email="j@e.com",
                        phone="12345678901234567890")
        assert m2.phone == "12345678901234567890"


# ============================================================================
# Field Constraints Tests
# ============================================================================

class TestFieldConstraints:
    """Tests for field constraints (min_length, max_length, default values)"""

    def test_name_length_constraints(self):
        """Test name field min_length=1 and max_length=255 constraints."""
        with pytest.raises(ValidationError):
            MemberBase(name="", email="j@e.com")

        with pytest.raises(ValidationError):
            MemberBase(name="a" * 256, email="j@e.com")

        # Valid at boundaries
        m1 = MemberBase(name="a", email="j@e.com")
        assert len(m1.name) == 1

        m2 = MemberBase(name="a" * 255, email="j@e.com")
        assert len(m2.name) == 255

    def test_email_length_constraints(self):
        """Test email field min_length=1 and max_length=255 constraints."""
        with pytest.raises(ValidationError):
            MemberBase(name="John", email="")

        with pytest.raises(ValidationError):
            MemberBase(name="John", email="a" * 250 + "@example.com")

    def test_phone_max_length_constraint(self):
        """Test phone field max_length=20 constraint."""
        with pytest.raises(ValidationError):
            MemberBase(name="John", email="j@e.com", phone="a" * 21)

    def test_active_field_defaults_and_assignment(self):
        """Test active field defaults to True and can be set to False."""
        m1 = MemberBase(name="John", email="j@e.com")
        assert m1.active is True

        m2 = MemberBase(name="John", email="j@e.com", active=False)
        assert m2.active is False


# ============================================================================
# Config Tests
# ============================================================================

class TestMemberBaseConfig:
    """Tests for MemberBase Config class settings"""

    def test_config_whitespace_stripping_with_validators(self):
        """Test Config.str_strip_whitespace = True works with validator normalization."""
        m = MemberBase(
            name="  John Doe  ",
            email="  JOHN@EXAMPLE.COM  ",
            phone="  (555) 123-4567  "
        )
        assert m.name == "John Doe"
        assert m.email == "john@example.com"
        assert m.phone == "(555) 123-4567"


# ============================================================================
# Happy Path Tests (Valid Inputs)
# ============================================================================

class TestMemberBaseHappyPath:
    """Tests with clean, valid inputs"""

    def test_all_fields_with_valid_values(self):
        """Test all fields with clean, valid values."""
        m = MemberBase(
            name="John Doe",
            email="john.doe@example.com",
            phone="(555) 123-4567",
            active=True
        )
        assert m.name == "John Doe"
        assert m.email == "john.doe@example.com"
        assert m.phone == "(555) 123-4567"
        assert m.active is True

    def test_all_fields_without_optional_phone(self):
        """Test all fields valid without phone (optional field)."""
        m = MemberBase(
            name="Jane Smith",
            email="jane@example.com"
        )
        assert m.name == "Jane Smith"
        assert m.email == "jane@example.com"
        assert m.phone is None
        assert m.active is True

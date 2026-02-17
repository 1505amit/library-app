"""Unit tests for BookBase field validators in book schema.

Tests cover the field validators in BookBase:
- normalize_text: @field_validator('title', 'author', mode='after') - strips whitespace
- Field constraints: min_length, max_length, range validation (published_year), default values
- Config: str_strip_whitespace = True
"""
import pytest
from pydantic import ValidationError

from app.schemas.book import BookBase


# ============================================================================
# normalize_text Validator Tests
# ============================================================================

class TestNormalizeTextValidator:
    """Tests for @field_validator('title', 'author') - normalize_text function"""

    def test_normalizes_title_whitespace(self):
        """Test normalize_text strips whitespace from title."""
        b = BookBase(title="  The Great Gatsby  ",
                     author="F. Scott Fitzgerald")
        assert b.title == "The Great Gatsby"

    def test_normalizes_author_whitespace(self):
        """Test normalize_text strips whitespace from author."""
        b = BookBase(title="1984", author="  George Orwell  ")
        assert b.author == "George Orwell"

    def test_preserves_internal_spaces(self):
        """Test normalize_text preserves internal spaces in title and author."""
        b = BookBase(title="A Tale  of  Two Cities", author="Charles  Dickens")
        assert b.title == "A Tale  of  Two Cities"
        assert b.author == "Charles  Dickens"

    def test_normalizes_both_title_and_author(self):
        """Test normalize_text strips both title and author simultaneously."""
        b = BookBase(title="  Pride and Prejudice  ", author="  Jane Austen  ")
        assert b.title == "Pride and Prejudice"
        assert b.author == "Jane Austen"


# ============================================================================
# Field Constraints Tests
# ============================================================================

class TestFieldConstraints:
    """Tests for field constraints (min_length, max_length, range validation, defaults)"""

    def test_title_min_length_constraint(self):
        """Test title field min_length=1 constraint."""
        with pytest.raises(ValidationError):
            BookBase(title="", author="Author")

    def test_title_max_length_constraint(self):
        """Test title field max_length=255 constraint."""
        with pytest.raises(ValidationError):
            BookBase(title="a" * 256, author="Author")

    def test_author_min_length_constraint(self):
        """Test author field min_length=1 constraint."""
        with pytest.raises(ValidationError):
            BookBase(title="Title", author="")

    def test_author_max_length_constraint(self):
        """Test author field max_length=255 constraint."""
        with pytest.raises(ValidationError):
            BookBase(title="Title", author="a" * 256)

    def test_published_year_minimum_constraint(self):
        """Test published_year field ge=1000 constraint."""
        with pytest.raises(ValidationError):
            BookBase(title="Title", author="Author", published_year=999)

    def test_published_year_maximum_constraint(self):
        """Test published_year field le=2100 constraint."""
        with pytest.raises(ValidationError):
            BookBase(title="Title", author="Author", published_year=2101)

    def test_published_year_optional_and_defaults_none(self):
        """Test published_year is optional and defaults to None."""
        b = BookBase(title="Title", author="Author")
        assert b.published_year is None

    def test_available_defaults_true(self):
        """Test available field defaults to True and can be set to False."""
        b1 = BookBase(title="Title", author="Author")
        assert b1.available is True

        b2 = BookBase(title="Title", author="Author", available=False)
        assert b2.available is False


# ============================================================================
# Config Tests
# ============================================================================

class TestBookBaseConfig:
    """Tests for BookBase Config class settings"""

    def test_config_str_strip_whitespace_with_validators(self):
        """Test Config.str_strip_whitespace = True works with validator normalization."""
        b = BookBase(
            title="  Crime and Punishment  ",
            author="  Fyodor Dostoevsky  ",
            published_year=1866,
            available=True
        )
        assert b.title == "Crime and Punishment"
        assert b.author == "Fyodor Dostoevsky"


# ============================================================================
# Happy Path Tests (Valid Inputs)
# ============================================================================

class TestBookBaseHappyPath:
    """Tests with clean, valid inputs"""

    def test_all_fields_with_valid_values(self):
        """Test all fields with clean, valid values."""
        b = BookBase(
            title="Moby Dick",
            author="Herman Melville",
            published_year=1851,
            available=True
        )
        assert b.title == "Moby Dick"
        assert b.author == "Herman Melville"
        assert b.published_year == 1851
        assert b.available is True

    def test_all_fields_without_optional_published_year(self):
        """Test all fields valid without published_year (optional field)."""
        b = BookBase(
            title="Harry Potter and the Philosopher's Stone",
            author="J.K. Rowling"
        )
        assert b.title == "Harry Potter and the Philosopher's Stone"
        assert b.author == "J.K. Rowling"
        assert b.published_year is None
        assert b.available is True

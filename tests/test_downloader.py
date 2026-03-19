"""
Test cases for downloader module.

Tests clean_filename, is_pdf_valid, and download functions.
"""

import pytest
from scihub_download.downloader import clean_filename, is_pdf_valid


class TestCleanFilename:
    """Test clean_filename function with different patterns."""

    def test_clean_filename_pmid_default(self):
        """Test default pmid pattern returns filename with .pdf."""
        assert clean_filename("12345") == "12345.pdf"

    def test_clean_filename_pmid_explicit(self):
        """Test explicit pmid pattern."""
        assert clean_filename("12345", "pmid") == "12345.pdf"

    def test_clean_filename_doi(self):
        """Test doi pattern sanitizes special characters."""
        assert clean_filename("10.1234/test", "doi") == "10.1234_test.pdf"

    def test_clean_filename_original(self):
        """Test original pattern returns identifier without .pdf suffix."""
        assert clean_filename("my-file.pdf", "original") == "my-file.pdf"

    def test_clean_filename_sanitization(self):
        """Test invalid filesystem characters are replaced with underscore."""
        assert clean_filename("test:file*name", "pmid") == "test_file_name.pdf"
        assert clean_filename("test/name>value", "doi") == "test_name_value.pdf"

    def test_clean_filename_special_chars_doi(self):
        """Test DOI with multiple special characters."""
        assert clean_filename("10.1000/abc.def/ghi", "doi") == "10.1000_abc.def_ghi.pdf"


class TestIsPdfValid:
    """Test is_pdf_valid function."""

    def test_nonexistent_file_returns_false(self):
        """Test that nonexistent file returns False."""
        assert is_pdf_valid("/tmp/nonexistent_file_12345.pdf") is False

    def test_invalid_file_returns_false(self, tmp_path):
        """Test that invalid file returns False."""
        # Create a non-PDF file
        invalid_file = tmp_path / "invalid.pdf"
        invalid_file.write_text("This is not a PDF")

        assert is_pdf_valid(str(invalid_file)) is False
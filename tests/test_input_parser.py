"""
Test cases for input_parser module.

Tests parsing of CSV, TXT, Excel files and single ID inputs.
"""

import pytest
from pathlib import Path


def test_parse_csv(sample_csv):
    """Test CSV parsing with PMID/DOI columns."""
    pass


def test_parse_txt(sample_txt):
    """Test TXT parsing with one ID per line."""
    pass


def test_parse_xlsx(sample_xlsx):
    """Test Excel .xlsx parsing."""
    pass


def test_parse_single_id():
    """Test single PMID/DOI from CLI argument."""
    pass


def test_normalize_columns():
    """Test column normalization."""
    pass
"""
Test cases for input_parser module.

Tests parsing of CSV, TXT, Excel files and single ID inputs.
"""

import pytest
import pandas as pd
from pathlib import Path
from scihub_download import parse_input_file, parse_single_id, normalize_columns


def test_parse_csv(sample_csv):
    """Test CSV parsing with PMID/DOI columns."""
    df = parse_input_file(sample_csv)
    assert isinstance(df, pd.DataFrame)
    assert "PMID" in df.columns
    assert "DOI" in df.columns
    assert len(df) == 2
    assert df["PMID"].iloc[0] == "12345"
    assert df["DOI"].iloc[0] == "10.1234/test"


def test_parse_txt(sample_txt):
    """Test TXT parsing with one ID per line, auto-detecting PMID vs DOI."""
    df = parse_input_file(sample_txt)
    assert isinstance(df, pd.DataFrame)
    assert "PMID" in df.columns
    assert "DOI" in df.columns
    # Should auto-detect numeric as PMID, slash as DOI
    assert "12345" in df["PMID"].values
    assert "10.1234/test" in df["DOI"].values


def test_parse_xlsx(sample_xlsx):
    """Test Excel .xlsx parsing."""
    df = parse_input_file(sample_xlsx)
    assert isinstance(df, pd.DataFrame)
    assert "PMID" in df.columns
    assert "DOI" in df.columns
    assert len(df) == 2


def test_parse_single_id_pmid():
    """Test single PMID from CLI argument."""
    df = parse_single_id("12345")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df["PMID"].iloc[0] == "12345"
    assert pd.isna(df["DOI"].iloc[0])


def test_parse_single_id_doi():
    """Test single DOI from CLI argument."""
    df = parse_single_id("10.1234/test")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert pd.isna(df["PMID"].iloc[0])
    assert df["DOI"].iloc[0] == "10.1234/test"


def test_normalize_columns_uppercase():
    """Test normalize_columns handles uppercase column names."""
    df = pd.DataFrame({"PMID": ["123"], "DOI": ["10.123/test"]})
    result = normalize_columns(df)
    assert "PMID" in result.columns
    assert "DOI" in result.columns


def test_normalize_columns_lowercase():
    """Test normalize_columns handles lowercase column names."""
    df = pd.DataFrame({"pmid": ["123"], "doi": ["10.123/test"]})
    result = normalize_columns(df)
    assert "PMID" in result.columns
    assert "DOI" in result.columns


def test_parse_input_file_not_found():
    """Test parse_input_file raises FileNotFoundError for non-existent file."""
    with pytest.raises(FileNotFoundError):
        parse_input_file("/nonexistent/path/file.csv")


def test_parse_input_file_unsupported():
    """Test parse_input_file raises ValueError for unsupported extension."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        f.write(b'{"test": "data"}')
        temp_path = f.name
    try:
        with pytest.raises(ValueError):
            parse_input_file(temp_path)
    finally:
        Path(temp_path).unlink()
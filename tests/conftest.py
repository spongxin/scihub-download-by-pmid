"""
Shared pytest fixtures for SciHub Downloader tests.

Provides test data fixtures for CSV, TXT, XLSX, and mixed format files.
"""

import pandas as pd
import pytest
from pathlib import Path


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing with PMID and DOI columns."""
    csv_file = tmp_path / "test.csv"
    df = pd.DataFrame({
        "PMID": ["12345", "67890"],
        "DOI": ["10.1234/test", "10.5678/example"]
    })
    df.to_csv(csv_file, index=False)
    return str(csv_file)


@pytest.fixture
def sample_txt(tmp_path):
    """Create a sample TXT file for testing with one PMID/DOI per line."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("12345\n67890\n10.1234/test\n10.5678/example\n")
    return str(txt_file)


@pytest.fixture
def sample_xlsx(tmp_path):
    """Create a sample Excel file for testing with PMID and DOI columns."""
    xlsx_file = tmp_path / "test.xlsx"
    df = pd.DataFrame({
        "PMID": ["12345", "67890"],
        "DOI": ["10.1234/test", "10.5678/example"]
    })
    df.to_excel(xlsx_file, index=False)
    return str(xlsx_file)


@pytest.fixture
def sample_mixed_txt(tmp_path):
    """Create a sample TXT file with mixed PMIDs and DOIs."""
    txt_file = tmp_path / "mixed.txt"
    # Mix of numeric PMIDs and DOI-style strings
    txt_file.write_text("12345\n10.1234/test\n67890\n10.5678/example\n")
    return str(txt_file)
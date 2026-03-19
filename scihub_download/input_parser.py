"""Input parsing module for SciHub Downloader."""

import pandas as pd
from pathlib import Path
from typing import Union


def parse_input_file(filepath: str) -> pd.DataFrame:
    """Parse input file and return DataFrame with PMID and DOI columns.

    Args:
        filepath: Path to input file (.csv, .txt, .xlsx, .xls)

    Returns:
        DataFrame with PMID and DOI columns

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file format is not supported
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")

    ext = path.suffix.lower()

    if ext == ".csv":
        df = pd.read_csv(filepath, dtype=str)
    elif ext == ".txt":
        df = pd.read_csv(filepath, header=None, names=["id"], dtype=str)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(filepath, dtype=str, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return normalize_columns(df)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure DataFrame has PMID and DOI columns.

    Handles:
    - Upper/lowercase column names (pmid/PMID, doi/DOI)
    - Missing columns (initializes to None)
    - Single-column input (auto-detects PMID vs DOI)
    - Files with only PMID or only DOI column

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with only PMID and DOI columns
    """
    # Convert column names to uppercase and strip whitespace
    df.columns = df.columns.str.upper().str.strip()

    # Initialize PMID and DOI columns if missing
    if "PMID" not in df.columns:
        df["PMID"] = None
    if "DOI" not in df.columns:
        df["DOI"] = None

    # Handle single-column files (e.g., TXT with one ID per line, or CSV with only PMID/DOI)
    id_columns = [c for c in df.columns if c not in ("PMID", "DOI")]

    # Case 1: Single column named "ID" - auto-detect by content
    if len(id_columns) == 1 and "ID" in df.columns:
        col = "ID"
        # DOI contains "/", PMID is numeric
        df.loc[df[col].str.contains("/", na=False), "DOI"] = df[col]
        df.loc[~df[col].str.contains("/", na=False), "PMID"] = df[col]

    # Case 2: Only PMID column provided (no DOI column in original file)
    elif "PMID" in df.columns and "DOI" not in df.columns and len(id_columns) == 0:
        # PMID only - DOI stays None
        pass

    # Case 3: Only DOI column provided (no PMID column in original file)
    elif "DOI" in df.columns and "PMID" not in df.columns and len(id_columns) == 0:
        # DOI only - PMID stays None
        pass

    # Case 4: Multiple id columns - try to auto-detect PMID vs DOI by content
    elif len(id_columns) > 0:
        for col in id_columns:
            # Skip if already processed
            if col not in df.columns:
                continue
            # Auto-detect: DOI contains "/", PMID is typically numeric
            mask_has_slash = df[col].str.contains("/", na=False)
            df.loc[mask_has_slash, "DOI"] = df.loc[mask_has_slash, col]
            df.loc[~mask_has_slash, "PMID"] = df.loc[~mask_has_slash, col]

    return df[["PMID", "DOI"]]


def parse_single_id(identifier: str) -> pd.DataFrame:
    """Parse single PMID or DOI from command line.

    Args:
        identifier: PMID (numeric) or DOI (contains "/")

    Returns:
        DataFrame with single row containing PMID or DOI
    """
    if "/" in identifier:
        return pd.DataFrame({"PMID": [None], "DOI": [identifier]})
    else:
        return pd.DataFrame({"PMID": [identifier], "DOI": [None]})
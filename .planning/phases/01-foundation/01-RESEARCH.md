# Phase 1: Foundation - Research

**Researched:** 2026-03-19
**Domain:** Python CLI development, multi-format file parsing
**Confidence:** HIGH

## Summary

This phase focuses on building a robust CLI interface using Python's argparse library and implementing multi-format input support (CSV, TXT, Excel, CLI argument). The existing codebase already uses argparse and pandas for CSV reading, so the work extends these patterns rather than introducing new paradigms.

**Primary recommendation:** Extend the existing argparse setup with subcommands or grouped arguments, use pandas for all file formats (CSV/TXT/Excel), and establish pytest infrastructure from the start.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INPUT-01 | CSV format with PMID/DOI columns | Pandas `read_csv()` - already implemented |
| INPUT-02 | TXT format (one ID per line) | Pandas `read_csv(header=None)` or standard file reading |
| INPUT-03 | Excel format (.xlsx) | Pandas `read_excel()` with openpyxl engine |
| INPUT-04 | Direct PMID/DOI via CLI argument | argparse positional or `--id` argument |
| CLI-01 | --verbose/-v flag | argparse `store_true` with mutually exclusive group for -v/-q |
| CLI-02 | --quiet/-q flag | argparse `store_true` with mutually exclusive group for -v/-q |
| CLI-03 | --workers/-w flag | Already implemented in existing code |
| CLI-04 | --output/-o flag | argparse with default value, path validation |
| CLI-05 | --format/-f flag | argparse choices for filename pattern |
| CLI-06 | Help message with all options | argparse auto-generates from descriptions |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `argparse` | stdlib | CLI argument parsing | Python standard library, zero dependencies |
| `pandas` | 2.x | File I/O (CSV, Excel, TXT) | Already used, handles all target formats |
| `openpyxl` | 3.x | Excel .xlsx backend for pandas | Required dependency for `read_excel()` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | 8.x | Test framework | All unit/integration tests |
| `pytest-cov` | 5.x | Coverage reporting | Optional, for coverage metrics |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| argparse | click | click has better decorator syntax but adds dependency; argparse is sufficient for this scope |
| argparse | typer | typer is modern but requires type hints everywhere; argparse matches existing code style |
| pandas for TXT | Pure Python file read | Simpler but less consistent; pandas approach unifies all input handling |

**Installation:**
```bash
pip install pandas openpyxl pytest pytest-cov
```

**Note:** `requests`, `pymupdf` (fitz), and `tqdm` are already dependencies from existing code.

## Architecture Patterns

### Recommended Project Structure
```
scihub-download-by-pmid/
├── scihub_download/
│   ├── __init__.py
│   ├── cli.py           # ArgumentParser setup and main entry
│   ├── input_parser.py  # Multi-format input handling
│   ├── downloader.py    # Download logic (Phase 3)
│   └── utils.py         # Helper functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Shared fixtures
│   ├── test_cli.py      # CLI argument tests
│   └── test_input_parser.py  # Input parsing tests
├── pyproject.toml       # Project configuration
└── README.md
```

### Pattern 1: Argparse Mutually Exclusive Groups
**What:** Prevent users from specifying both --verbose and --quiet simultaneously.
**When to use:** For mutually exclusive boolean flags.
**Example:**
```python
# Source: Python stdlib argparse documentation
import argparse

parser = argparse.ArgumentParser(description="SciHub PDF Downloader")

# Create mutually exclusive group for verbosity
verbosity = parser.add_mutually_exclusive_group()
verbosity.add_argument("-v", "--verbose", action="store_true",
                       help="Enable detailed output")
verbosity.add_argument("-q", "--quiet", action="store_true",
                       help="Suppress non-essential output")
```

### Pattern 2: Flexible Input Source
**What:** Accept input from file or direct argument, with format auto-detection.
**When to use:** When supporting multiple input formats.
**Example:**
```python
# Input group - file or direct ID, not both
input_group = parser.add_mutually_exclusive_group(required=True)
input_group.add_argument("-f", "--file", type=str,
                         help="Input file (CSV, TXT, or XLSX)")
input_group.add_argument("--id", type=str,
                         help="Single PMID or DOI to download")
input_group.add_argument("csv_file", nargs="?",  # Keep backward compat
                         help="CSV file (legacy positional argument)")

# Format detection based on extension
def detect_input_format(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    return {"csv": "csv", ".txt": "txt", ".xlsx": "excel"}.get(ext, "csv")
```

### Pattern 3: Pandas Unified Input Handler
**What:** Use pandas for all file formats with consistent output schema.
**When to use:** When multiple file formats need unified processing.
**Example:**
```python
import pandas as pd
from pathlib import Path

def parse_input_file(filepath: str) -> pd.DataFrame:
    """Parse input file and return DataFrame with 'id' column."""
    ext = Path(filepath).suffix.lower()

    if ext == ".csv":
        df = pd.read_csv(filepath, dtype=str)
    elif ext == ".xlsx":
        df = pd.read_excel(filepath, dtype=str, engine="openpyxl")
    elif ext == ".txt":
        # One ID per line, no header
        df = pd.read_csv(filepath, header=None, names=["id"], dtype=str)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    return normalize_columns(df)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure DataFrame has PMID and DOI columns."""
    df.columns = df.columns.str.upper().str.strip()
    if "PMID" not in df.columns:
        df["PMID"] = None
    if "DOI" not in df.columns:
        df["DOI"] = None
    # Handle single-column input (from TXT)
    if len(df.columns) == 1:
        col = df.columns[0]
        # Auto-detect: if looks like DOI, put in DOI; else PMID
        df["id"] = df[col]
        df.loc[df["id"].str.contains("/", na=False), "DOI"] = df["id"]
        df.loc[~df["id"].str.contains("/", na=False), "PMID"] = df["id"]
    return df
```

### Pattern 4: pytest CLI Testing
**What:** Test argparse applications using subprocess or monkeypatching.
**When to use:** For validating CLI argument parsing.
**Example:**
```python
# Using pytest and monkeypatch
import pytest
from scihub_download.cli import create_parser

def test_verbose_quiet_mutually_exclusive():
    """Test that -v and -q cannot be used together."""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["-v", "-q", "test.csv"])

def test_help_shows_all_options(capsys):
    """Test that --help displays all documented options."""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    captured = capsys.readouterr()
    assert "--verbose" in captured.out
    assert "--quiet" in captured.out
    assert "--workers" in captured.out
```

### Anti-Patterns to Avoid
- **Positional arguments with too many meanings:** The current code uses `csv_file` as positional. For new inputs, prefer explicit `--file` flag.
- **Hardcoded format detection by content:** Always use file extension for format detection; trying to parse content to guess format is error-prone.
- **Exit codes as strings:** Use `sys.exit(1)` for errors, not just printing and returning.
- **Missing type hints:** All functions should have type hints per PEP 8 conventions.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSV parsing | Custom split-by-comma | `pandas.read_csv()` | Handles quotes, escaping, encodings |
| Excel reading | Custom XML parsing | `pandas.read_excel()` | Complex xlsx format, openpyxl handles it |
| CLI argument parsing | sys.argv parsing | `argparse.ArgumentParser` | Handles help, validation, types |
| Format detection | Magic number checks | `pathlib.Path.suffix` | Simple and reliable for known formats |
| Verbosity control | Custom print statements | `logging` module with level setting | Thread-safe, configurable output |

**Key insight:** Pandas already handles CSV, TXT, and Excel with a unified API. Using pandas for all input formats means consistent error handling and data normalization.

## Common Pitfalls

### Pitfall 1: Mutually Exclusive Arguments Not Enforced
**What goes wrong:** Users specify both --verbose and --quiet, leading to undefined behavior.
**Why it happens:** Using separate `add_argument` calls instead of `add_mutually_exclusive_group`.
**How to avoid:** Always use `parser.add_mutually_exclusive_group()` for conflicting flags.
**Warning signs:** If statement chains checking multiple flags to determine mode.

### Pitfall 2: Excel Dependency Missing
**What goes wrong:** `pd.read_excel()` fails with "Missing optional dependency 'openpyxl'".
**Why it happens:** openpyxl is not installed by default with pandas.
**How to avoid:** Document openpyxl in requirements, catch ImportError with helpful message.
**Warning signs:** Code runs in dev but fails in fresh environment.

### Pitfall 3: Encoding Issues with TXT Files
**What goes wrong:** UnicodeDecodeError when reading TXT files with non-ASCII characters.
**Why it happens:** Default encoding varies by platform (UTF-8 on Linux, cp1252 on Windows).
**How to avoid:** Always specify `encoding="utf-8"` when opening text files, or let pandas handle it.
**Warning signs:** Files work on one OS but fail on another.

### Pitfall 4: argparse Backward Compatibility
**What goes wrong:** Existing users have scripts calling the old positional argument format.
**Why it happens:** Changing CLI interface breaks existing workflows.
**How to avoid:** Use `nargs="?"` for optional positional arguments, or add deprecation warnings.
**Warning signs:** Breaking change in argument structure without migration path.

### Pitfall 5: Single ID Input Validation
**What goes wrong:** Users provide invalid PMID/DOI formats that cause downstream errors.
**Why it happens:** No validation at input stage.
**How to avoid:** Add basic format validation (PMID: numeric, DOI: contains `/`).
**Warning signs:** Cryptic error messages from download function instead of input function.

## Code Examples

### Complete argparse Setup for Phase 1
```python
import argparse
import sys
from pathlib import Path

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="scihub-download",
        description="Download PDFs from Sci-Hub using PMID/DOI identifiers.",
        epilog="Example: scihub-download --file papers.csv --output ./pdfs"
    )

    # Mutually exclusive input group
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-f", "--file",
        type=str,
        metavar="PATH",
        help="Input file (CSV, TXT, or XLSX format)"
    )
    input_group.add_argument(
        "--id",
        type=str,
        metavar="IDENTIFIER",
        help="Single PMID or DOI to download"
    )

    # Output options
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./pdfs",
        metavar="DIR",
        help="Output directory for PDFs (default: ./pdfs)"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=5,
        metavar="N",
        help="Number of parallel download threads (default: 5)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["pmid", "doi", "original"],
        default="pmid",
        help="Filename pattern: pmid, doi, or original (default: pmid)"
    )

    # Verbosity (mutually exclusive)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed output"
    )
    verbosity.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-essential output"
    )

    return parser
```

### Input Parsing with Format Detection
```python
import pandas as pd
from pathlib import Path
from typing import Union

def parse_input_file(filepath: str) -> pd.DataFrame:
    """
    Parse input file and return DataFrame with PMID and DOI columns.

    Supports CSV, TXT, and XLSX formats.

    Args:
        filepath: Path to input file

    Returns:
        DataFrame with 'PMID' and 'DOI' columns (may contain None)

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file format is unsupported
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")

    ext = path.suffix.lower()

    if ext == ".csv":
        df = pd.read_csv(filepath, dtype=str)
    elif ext == ".txt":
        # One ID per line, no header
        df = pd.read_csv(filepath, header=None, names=["id"], dtype=str)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(filepath, dtype=str, engine="openpyxl")
    else:
        raise ValueError(
            f"Unsupported file format: {ext}. "
            "Supported formats: .csv, .txt, .xlsx"
        )

    return normalize_columns(df)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure DataFrame has PMID and DOI columns."""
    # Clean column names
    df.columns = df.columns.str.upper().str.strip()

    # Initialize missing columns
    if "PMID" not in df.columns:
        df["PMID"] = None
    if "DOI" not in df.columns:
        df["DOI"] = None

    # Handle single-column input (from TXT or single-column CSV)
    id_columns = [c for c in df.columns if c not in ("PMID", "DOI")]
    if len(id_columns) == 1:
        col = id_columns[0]
        # Auto-detect format: DOIs contain '/', PMIDs are numeric
        df.loc[df[col].str.contains("/", na=False), "DOI"] = df[col]
        df.loc[~df[col].str.contains("/", na=False), "PMID"] = df[col]

    return df[["PMID", "DOI"]]
```

### Single ID Argument Handler
```python
def parse_single_id(identifier: str) -> pd.DataFrame:
    """
    Parse single PMID or DOI from command line.

    Args:
        identifier: PMID (numeric) or DOI (contains /)

    Returns:
        Single-row DataFrame with PMID and DOI columns
    """
    if "/" in identifier:
        # Looks like a DOI
        return pd.DataFrame({"PMID": [None], "DOI": [identifier]})
    else:
        # Assume PMID
        return pd.DataFrame({"PMID": [identifier], "DOI": [None]})
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `sys.argv` manual parsing | `argparse` module | Python 2.7+ | Type conversion, help generation, validation |
| `xlrd` for Excel | `openpyxl` engine | pandas 1.0+ | Better xlsx support, maintained |
| Print statements for logging | `logging` module | Python 2.3+ | Levels, handlers, formatting |

**Deprecated/outdated:**
- `optparse`: Replaced by argparse in Python 2.7+
- `xlrd` engine for xlsx: Use openpyxl instead (xlrd only supports .xls now)

## Open Questions

1. **Should we maintain backward compatibility with the positional `csv_file` argument?**
   - What we know: Existing code uses `parser.add_argument("csv_file", ...)`
   - What's unclear: Whether existing users have scripts relying on this format
   - Recommendation: Use `nargs="?"` to make it optional while supporting new `--file` flag, add deprecation warning in Phase 1, remove in v2

2. **How should TXT files with mixed PMIDs and DOIs be handled?**
   - What we know: Some users may have files with both identifiers mixed
   - What's unclear: Should we auto-detect per-line or require consistent format
   - Recommendation: Auto-detect per-line (DOI contains `/`, PMID is numeric)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | None - use pytest's auto-discovery |
| Quick run command | `pytest tests/ -v` |
| Full suite command | `pytest tests/ -v --cov=scihub_download` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| INPUT-01 | Parse CSV with PMID/DOI columns | unit | `pytest tests/test_input_parser.py::test_parse_csv -v` | Wave 0 |
| INPUT-02 | Parse TXT with one ID per line | unit | `pytest tests/test_input_parser.py::test_parse_txt -v` | Wave 0 |
| INPUT-03 | Parse Excel .xlsx file | unit | `pytest tests/test_input_parser.py::test_parse_xlsx -v` | Wave 0 |
| INPUT-04 | Parse single PMID/DOI from CLI | unit | `pytest tests/test_input_parser.py::test_parse_single_id -v` | Wave 0 |
| CLI-01 | --verbose/-v flag works | unit | `pytest tests/test_cli.py::test_verbose_flag -v` | Wave 0 |
| CLI-02 | --quiet/-q flag works | unit | `pytest tests/test_cli.py::test_quiet_flag -v` | Wave 0 |
| CLI-03 | --workers/-w flag works | unit | `pytest tests/test_cli.py::test_workers_flag -v` | Wave 0 |
| CLI-04 | --output/-o flag works | unit | `pytest tests/test_cli.py::test_output_flag -v` | Wave 0 |
| CLI-05 | --format/-f flag works | unit | `pytest tests/test_cli.py::test_format_flag -v` | Wave 0 |
| CLI-06 | Help shows all options | unit | `pytest tests/test_cli.py::test_help_message -v` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -v`
- **Per wave merge:** `pytest tests/ -v --cov=scihub_download`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/__init__.py` - Test package initialization
- [ ] `tests/conftest.py` - Shared fixtures (sample CSV, TXT, XLSX files)
- [ ] `tests/test_cli.py` - CLI argument parsing tests (covers CLI-01 to CLI-06)
- [ ] `tests/test_input_parser.py` - Input parsing tests (covers INPUT-01 to INPUT-04)
- [ ] `pytest` and `pytest-cov` installation: `pip install pytest pytest-cov`

### Test Fixtures Needed
```python
# tests/conftest.py
import pytest
import pandas as pd
from pathlib import Path
import tempfile

@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("PMID,DOI\n12345,10.1234/test\n")
    return str(csv_file)

@pytest.fixture
def sample_txt(tmp_path):
    """Create a sample TXT file for testing."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("12345\n10.5678/example\n")
    return str(txt_file)

@pytest.fixture
def sample_xlsx(tmp_path):
    """Create a sample Excel file for testing."""
    df = pd.DataFrame({"PMID": ["12345"], "DOI": ["10.1234/test"]})
    xlsx_file = tmp_path / "test.xlsx"
    df.to_excel(xlsx_file, index=False)
    return str(xlsx_file)
```

## Sources

### Primary (HIGH confidence)
- Python stdlib `argparse` documentation - argument parsing patterns
- pandas documentation - read_csv, read_excel, read_fwf
- Existing codebase (`scihub_download_chenwei.py`) - current patterns

### Secondary (MEDIUM confidence)
- pytest documentation patterns for CLI testing
- openpyxl as pandas Excel backend (standard approach)

### Tertiary (LOW confidence)
- None identified - all recommendations based on standard library or existing dependencies

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Uses existing dependencies (argparse, pandas) plus one well-known addition (openpyxl)
- Architecture: HIGH - argparse patterns are well-documented Python stdlib
- Pitfalls: HIGH - Common issues with file encoding, Excel dependencies, and CLI design are well-known

**Research date:** 2026-03-19
**Valid until:** 6 months - argparse and pandas APIs are stable, openpyxl is mature
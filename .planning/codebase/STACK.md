# Tech Stack: SciHub Download by PMID

## Languages

- **Python 3** - Primary language for the download script

## Runtime

- Python 3.x with standard library modules

## Core Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP client for downloading PDFs |
| `pymupdf` (fitz) | PDF validation |
| `pandas` | CSV file reading/writing |
| `tqdm` | Progress bar for downloads |

## External Integrations

| Service | Purpose |
|---------|---------|
| Sci-Hub mirrors (multiple URLs) | PDF retrieval |
| Local filesystem | PDF storage |

## Configuration

- **Default Sci-Hub sources**: Configurable list of base URLs
- **User-Agent**: Custom header to mimic browser
- **Thread pool**: Default 5 workers for parallel downloads

## Entry Points

- `scihub_download_chenwei.py` - Main CLI script

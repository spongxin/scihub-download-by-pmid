# Architecture: SciHub Download by PMID

## Overview

A command-line tool for batch downloading PDF papers from Sci-Hub using PMID/DOI pairs from a CSV file.

## Architecture Pattern

**Single-tier CLI application** - All logic contained in one script with functional organization.

## Data Flow

```
CSV Input (PMID, DOI) → DOI Parser → Sci-Hub URL Generator → PDF Downloader → Local Storage
                                                                  ↓
                                                            PDF Validator
```

## Components

### 1. Configuration Layer
- `DEFAULT_SCI_HUB_SOURCES` - List of Sci-Hub mirror URLs
- `REQUESTS_SESSION` - Shared HTTP session with headers

### 2. Utility Functions
- `clean_filename()` - Sanitize PMID for filenames
- `is_pdf_valid()` - Validate downloaded PDFs using PyMuPDF
- `download_file()` - HTTP download with progress

### 3. Download Logic
- `download_worker()` - Main download logic per DOI
  - Tries multiple Sci-Hub mirrors
  - Extracts PDF URL from iframe/embed tags
  - Validates downloaded PDF

### 4. CLI Entry Point
- `main()` - Argument parsing and orchestration
  - CSV reading and validation
  - Pre-checks existing files
  - Parallel execution via ThreadPoolExecutor
  - Failed records tracking

## Threading Model

- **ThreadPoolExecutor** with configurable workers (default: 5)
- Parallel downloads with thread-safe logging

## Error Handling

- Try/except around all network operations
- Failed downloads tracked to separate CSV
- Corrupted PDF detection and optional re-download

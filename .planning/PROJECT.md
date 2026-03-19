# SciHub Downloader CLI

## What This Is

A robust command-line tool for batch downloading academic PDFs from Sci-Hub using PMID/DOI identifiers. Supports multiple input formats, dynamic source discovery, parallel downloads with rich progress display, and comprehensive error handling.

## Core Value

Reliably download PDFs from Sci-Hub with minimal user intervention — automatic source discovery, smart retries, and clear reporting make the process as smooth as possible.

## Requirements

### Validated

- ✓ Batch download PDFs from Sci-Hub using DOI — existing
- ✓ Parallel downloads with thread pool — existing
- ✓ CSV input with PMID/DOI columns — existing
- ✓ PDF validation — existing
- ✓ Failed download tracking — existing

### Active

- [ ] Multi-format input support (CSV, TXT, Excel)
- [ ] Dynamic SciHub source discovery from sci-hub.pub
- [ ] Source availability testing via actual download
- [ ] Automatic source switching on failure
- [ ] Smart retry strategy based on error type
- [ ] File renaming options (PMID, DOI, or simple patterns)
- [ ] Rich progress bar with parallel download display
- [ ] Configurable log levels (-v/--verbose)
- [ ] Terminal summary report with statistics
- [ ] Download report file generation
- [ ] CLI with comprehensive options and help

### Out of Scope

- Metadata fetching (titles, authors) — not needed for current use case
- OAuth/authentication — Sci-Hub requires no auth
- GUI interface — CLI only for this version
- Async/await refactoring — threading is sufficient

## Context

### Existing Codebase

Single Python script (`scihub_download_chenwei.py`) with:
- Hardcoded Sci-Hub mirror URLs
- ThreadPoolExecutor for parallel downloads
- Basic PDF validation via PyMuPDF
- CSV input with PMID/DOI columns

### Technical Environment

- Python 3.x
- Dependencies: requests, pymupdf, pandas, tqdm
- Target platforms: Linux, macOS, Windows

### Key Constraints

- Sci-Hub URLs change frequently — need dynamic discovery
- Network reliability varies — need robust error handling
- User may have large CSV files — performance matters

## Constraints

- **Tech Stack**: Python 3.8+ — broad compatibility
- **Dependencies**: Minimal external dependencies, standard packages preferred
- **Network**: Must handle unreliable connections gracefully

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use rich for progress bars | Better visual feedback than tqdm | — Pending |
| Smart retry by error type | Network errors vs 404s need different handling | — Pending |
| Auto source discovery | Manual URL maintenance is fragile | — Pending |
| No metadata fetching | User confirmed not needed, reduces complexity | — Pending |

---
*Last updated: 2026-03-19 after initialization*
# Phase 3: Download Engine - Research

**Researched:** 2026-03-19
**Domain:** Multi-threaded PDF downloads with progress display, validation, and smart retry logic
**Confidence:** HIGH

## Summary

Phase 3 implements the core download engine for reliable PDF downloading from Sci-Hub. The existing codebase already has substantial infrastructure: ThreadPoolExecutor for parallelism, tqdm for progress, and fitz (PyMuPDF) for PDF validation. The key enhancements needed are explicit error classification (404 vs network errors), proper retry counting (up to 3 retries), and structured error logging with error types and source URLs.

**Primary recommendation:** Enhance the existing `downloader.py` with explicit error classification, add retry counting, and implement structured logging. The foundation is solid—the work is about making the error handling more explicit and meeting the exact requirements (3 retries for network errors, skip 404s immediately).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Try all available sources once for each DOI (if all fail, mark as failed)
- Single aggregate progress bar (tqdm)
- Skip 404 errors immediately (not found = permanent failure)
- Retry network errors by trying next source
- Default: 5 worker threads, Maximum: 20 workers
- --workers flag already implemented in Phase 1

### Claude's Discretion
- Exact timeout values for downloads vs source checks
- Progress bar styling details
- How to handle validation failures (corrupted PDF after download)

### Deferred Ideas (OUT OF SCOPE)
None
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DL-01 | System downloads PDFs using multi-threading | ThreadPoolExecutor already implemented in downloader.py |
| DL-02 | System displays rich progress bar during downloads | tqdm already in use, single aggregate bar confirmed |
| DL-03 | System validates downloaded PDFs are not corrupted | fitz (PyMuPDF) already validates in `is_pdf_valid()` |
| DL-04 | System implements smart retry based on error type | Need to add explicit error classification |
| DL-05 | System retries network errors up to 3 times | Need to add retry counting per DOI |
| DL-06 | System does not retry 404/not found errors | Need to make 404 handling explicit |
</phase_requirements>

## Current State

### Existing Implementation Analysis

The current `downloader.py` has:
- `ThreadPoolExecutor` with max_workers parameter (lines 183-184)
- `tqdm` progress bar with `as_completed()` (line 185)
- `fitz` PDF validation via `is_pdf_valid()` (lines 46-56, 101-102)
- Source failover loop iterating over all sources (lines 83-108)
- Basic error handling with `requests.exceptions.RequestException` (line 71)

### Gap Analysis

| Component | Current State | Required State | Gap |
|-----------|---------------|----------------|-----|
| Multi-threading | Working | DL-01 | Complete |
| Progress bar | Working | DL-02 | Complete |
| PDF validation | Working | DL-03 | Complete |
| Error classification | Implicit | DL-04 | Need explicit classification |
| Retry counting | None | DL-05 | Need 3-retry logic |
| 404 handling | Implicit (skips to next source) | DL-06 | Need explicit 404 check |

## Standard Stack

### Core Libraries
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `requests` | >=2.0.0 | HTTP downloads | Industry standard, robust error handling |
| `tqdm` | >=4.0.0 | Progress bar | Already in use, single aggregate bar requirement |
| `fitz` (PyMuPDF) | >=1.20.0 | PDF validation | Already in use, reliable validation |

### Dependencies Already Satisfied
All required libraries are already in `pyproject.toml` and in use.

### Alternative Approaches Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `fitz` validation | `pdfminer.six` | More complex API, fitz is already working |
| tqdm | `click.progressbar` | Less flexible, tqdm already in use |
| ThreadPoolExecutor | `asyncio/aiohttp` | Async would require major refactor, threading sufficient |

## Architecture Patterns

### Recommended Project Structure
```
scihub_download/
├── __init__.py
├── cli.py                 # Already exists
├── input_parser.py        # Already exists
├── source_manager.py      # Already exists (Phase 2)
├── downloader.py          # Enhance for Phase 3
└── errors.py              # NEW: Error classification module
```

### Pattern 1: Error Classification
**What:** Classify download errors into categories for smart retry decisions
**When to use:** Every download attempt
**Example:**
```python
from enum import Enum
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError

class DownloadErrorType(Enum):
    NOT_FOUND = "404"           # Skip immediately, no retry
    NETWORK_ERROR = "network"   # Retry up to 3 times
    VALIDATION_FAILED = "validation"  # Retry with next source
    UNKNOWN = "unknown"         # Log and fail

def classify_error(exception: Exception, response=None) -> DownloadErrorType:
    """Classify error for retry decision making."""
    if isinstance(exception, HTTPError):
        if response and response.status_code == 404:
            return DownloadErrorType.NOT_FOUND
        return DownloadErrorType.NETWORK_ERROR
    if isinstance(exception, (Timeout, ConnectionError)):
        return DownloadErrorType.NETWORK_ERROR
    return DownloadErrorType.UNKNOWN
```

### Pattern 2: Retry with Source Failover
**What:** Try each source, retry network errors, skip on 404
**When to use:** In download_worker function
**Example:**
```python
MAX_RETRIES = 3

def download_with_retry(doi: str, pmid: str, sources: List[str], save_dir: str) -> bool:
    """Download with smart retry based on error type."""
    for source in sources:
        retry_count = 0
        while retry_count < MAX_RETRIES:
            error_type = download_single_source(doi, source, save_dir)

            if error_type == DownloadErrorType.NOT_FOUND:
                break  # Skip to next source immediately
            elif error_type == DownloadErrorType.NETWORK_ERROR:
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    continue  # Retry same source
            else:
                break  # Other errors: try next source

        # If successful on this source, return
        if is_pdf_valid(os.path.join(save_dir, clean_filename(pmid))):
            return True

    return False
```

### Pattern 3: Structured Error Logging
**What:** Log error type and source URL for debugging
**When to use:** When download fails
**Example:**
```python
def log_failure(pmid: str, doi: str, source_url: str, error_type: DownloadErrorType, error_msg: str):
    """Structured logging for failed downloads."""
    logging.warning(
        f"[FAILED] {pmid} | DOI: {doi} | "
        f"Error: {error_type.value} | Source: {source_url} | "
        f"Detail: {error_msg}"
    )
```

### Anti-Patterns to Avoid
- **Catching all exceptions broadly:** Leads to unclear error classification. Use specific exception types.
- **Retrying 404s:** Wastes time on permanent failures. Check status code before retry.
- **No retry limit:** Can cause infinite loops. Always cap retries at 3.
- **Logging only generic messages:** Makes debugging source issues difficult. Include error type and URL.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF validation | Custom parser | `fitz.open()` | Already handles corrupted/malformed PDFs reliably |
| Progress tracking | Custom implementation | `tqdm` with `as_completed()` | Thread-safe, already integrated |
| HTTP error handling | String parsing | `response.raise_for_status()` | Proper exception hierarchy |
| Thread pooling | Custom thread management | `ThreadPoolExecutor` | Already battle-tested |

**Key insight:** The existing code already uses the right libraries. The enhancement is in error classification logic, not new libraries.

## Common Pitfalls

### Pitfall 1: Not Distinguishing 404 from Network Errors
**What goes wrong:** Treating 404 as retryable causes unnecessary wait time
**Why it happens:** Using generic `RequestException` catch-all
**How to avoid:** Check `response.status_code == 404` before deciding to retry
**Warning signs:** Downloads take much longer than expected, high retry counts

### Pitfall 2: Retry Counting Per Source Instead of Per DOI
**What goes wrong:** Retrying same source 3 times when another source might work
**Why it happens:** Implementing retry at source level instead of DOI level
**How to avoid:** Track retries per DOI, try all sources before exhausting retries
**Warning signs:** First source fails repeatedly even when other sources work

### Pitfall 3: Race Condition in Progress Bar
**What goes wrong:** Progress bar updates from multiple threads cause garbled output
**Why it happens:** Not using tqdm's thread-safe API
**How to avoid:** Use `tqdm` with `as_completed()` which is thread-safe
**Warning signs:** Interleaved or missing progress bar updates

### Pitfall 4: Validation Before Complete Download
**What goes wrong:** Checking PDF validity while still writing
**Why it happens:** Not closing file handle before validation
**How to avoid:** Use context manager (`with open`) ensures file closed before validation

## Code Examples

### Enhanced download_worker with Error Classification
```python
# Source: Based on existing downloader.py + error classification pattern

class DownloadErrorType(Enum):
    NOT_FOUND = "404"
    NETWORK_ERROR = "network"
    VALIDATION_FAILED = "validation"
    SUCCESS = "success"

MAX_RETRIES = 3

def download_single_source(doi: str, source_url: str, filepath: str) -> DownloadErrorType:
    """Attempt download from a single source. Returns error type."""
    try:
        url_to_fetch = f"{source_url.rstrip('/')}/{doi}"
        resp = REQUESTS_SESSION.get(url_to_fetch, timeout=90)

        # Check for 404 before raising
        if resp.status_code == 404:
            return DownloadErrorType.NOT_FOUND

        resp.raise_for_status()

        # Extract PDF URL
        match = re.search(r'(?:iframe|embed).*?src="([^"]+\.pdf)', resp.text)
        if not match:
            return DownloadErrorType.NOT_FOUND  # No PDF available

        pdf_url = match.group(1)
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url
        elif not pdf_url.startswith("http"):
            pdf_url = f"{source_url.rstrip('/')}/{pdf_url.lstrip('/')}"

        # Download file
        if not download_file(pdf_url, filepath):
            return DownloadErrorType.NETWORK_ERROR

        # Validate PDF
        if not is_pdf_valid(filepath):
            os.remove(filepath)
            return DownloadErrorType.VALIDATION_FAILED

        return DownloadErrorType.SUCCESS

    except requests.exceptions.Timeout:
        return DownloadErrorType.NETWORK_ERROR
    except requests.exceptions.ConnectionError:
        return DownloadErrorType.NETWORK_ERROR
    except requests.exceptions.HTTPError:
        return DownloadErrorType.NETWORK_ERROR
    except Exception as e:
        logging.debug(f"Unexpected error from {source_url}: {e}")
        return DownloadErrorType.UNKNOWN


def download_worker(row, save_dir: str, sources: List[str]) -> bool:
    """Enhanced download worker with retry logic."""
    doi = row['DOI']
    pmid = row['PMID']
    filename = clean_filename(pmid)
    filepath = os.path.join(save_dir, filename)

    for source_url in sources:
        retry_count = 0
        while retry_count < MAX_RETRIES:
            error_type = download_single_source(doi, source_url, filepath)

            if error_type == DownloadErrorType.SUCCESS:
                logging.info(f"[SUCCESS] {pmid}")
                return True

            elif error_type == DownloadErrorType.NOT_FOUND:
                # Skip to next source immediately
                logging.debug(f"404 from {source_url}, trying next source")
                break

            elif error_type == DownloadErrorType.NETWORK_ERROR:
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    logging.debug(f"Network error from {source_url}, retry {retry_count}/{MAX_RETRIES}")
                    continue
                # Exhausted retries, try next source
                logging.debug(f"Exhausted retries for {source_url}")
                break

            else:
                # Validation failed or unknown - try next source
                break

        # If file exists and valid from this source, we're done
        if os.path.exists(filepath) and is_pdf_valid(filepath):
            return True

    # All sources exhausted
    logging.warning(f"[FAILED] {pmid} | DOI: {doi} | All sources failed")
    return False
```

### Progress Bar Integration (Already Working)
```python
# Source: Existing downloader.py line 185
# Already correctly uses as_completed which is thread-safe

with ThreadPoolExecutor(max_workers=args.workers) as executor:
    futures = {executor.submit(download_worker, row, args.save_dir, sources): row for row in df_to_download}
    for future in tqdm(as_completed(futures), total=len(futures), desc="下载 PDF", ncols=100):
        # Process results
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No error classification | Explicit error types | This phase | Enables smart retry |
| Retry all errors | Skip 404s, retry network | This phase | Faster failure detection |
| Generic exception catching | Specific exception handling | This phase | Better debugging |

**Deprecated/outdated:**
- None - this is an enhancement of existing working code

## Open Questions

1. **Timeout values**
   - What we know: Current code uses 90s for source check, 120s for download
   - What's unclear: Optimal timeout for different network conditions
   - Recommendation: Use 60s for source check, 120s for download (Claude's discretion)

2. **Validation failure handling**
   - What we know: Corrupted PDF should trigger retry
   - What's unclear: After validation failure, should we retry same source or next?
   - Recommendation: Move to next source on validation failure (current behavior)

3. **Progress bar styling**
   - What we know: Single aggregate bar with count only
   - What's unclear: Should we show per-DOI status?
   - Recommendation: Keep minimal - count only as per decisions

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >= 8.0.0 |
| Config file | pyproject.toml (tool.pytest.ini_options) |
| Quick run command | `pytest tests/ -x -v` |
| Full suite command | `pytest tests/ --cov=scihub_download --cov-report=term-missing` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| DL-01 | Multi-threading | Unit + Integration | `pytest tests/test_downloader.py::test_multithreading -x` | NEW file needed |
| DL-02 | Progress bar | Unit | `pytest tests/test_downloader.py::test_progress_bar -x` | NEW file needed |
| DL-03 | PDF validation | Unit | `pytest tests/test_downloader.py::test_pdf_validation -x` | NEW file needed |
| DL-04 | Smart retry | Unit | `pytest tests/test_downloader.py::test_error_classification -x` | NEW file needed |
| DL-05 | Retry count 3 | Unit | `pytest tests/test_downloader.py::test_retry_limit -x` | NEW file needed |
| DL-06 | Skip 404 | Unit | `pytest tests/test_downloader.py::test_skip_404 -x` | NEW file needed |

### Sampling Rate
- **Per task commit:** `pytest tests/test_downloader.py -x -q` (runs only new downloader tests)
- **Per wave merge:** `pytest tests/ -x -q` (all tests)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_downloader.py` — covers DL-01 through DL-06
- [ ] Mock fixtures for HTTP responses (404, network errors, valid PDF)
- [ ] Fixture for temp PDF with known content

**Existing test infrastructure covers:**
- `tests/conftest.py` — shared fixtures (needs sample PDF fixture added)
- `pyproject.toml` — pytest configuration (complete)

## Sources

### Primary (HIGH confidence)
- Existing codebase: `scihub_download/downloader.py` — current implementation
- Existing codebase: `scihub_download/source_manager.py` — Phase 2 source management
- `pyproject.toml` — dependencies and pytest config

### Secondary (MEDIUM confidence)
- requests library documentation — error handling patterns
- tqdm documentation — thread-safe progress bar usage

### Tertiary (LOW confidence)
- N/A — this is enhancement of existing working code

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in use and working
- Architecture: HIGH - Existing code provides solid foundation
- Pitfalls: HIGH - Common patterns well understood

**Research date:** 2026-03-19
**Valid until:** 90 days (stable domain - no major library changes expected)
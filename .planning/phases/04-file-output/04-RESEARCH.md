# Phase 4: File Output - Research

**Researched:** 2026-03-19
**Domain:** File output management, filename patterns, file integrity
**Confidence:** HIGH

## Summary

Phase 4 focuses on file output control. The codebase already has substantial implementation for all four requirements (OUT-01 through OUT-04), but there's a **critical gap**: the CLI `--format` flag is not connected to the downloader logic. The downloader always uses PMID-based filenames regardless of user preference.

**Primary recommendation:** Connect existing CLI `--format` flag to downloader, implement DOI and "original" filename patterns in `clean_filename()` function.

## User Constraints

There are no CONTEXT.md decisions for this phase - all options are open for planning.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| OUT-01 | User can specify output directory for PDFs | CLI already has `--output` flag (cli.py:28) |
| OUT-02 | User can choose filename pattern (PMID, DOI, or custom) | CLI has `--format` flag but not connected to downloader |
| OUT-03 | System skips already downloaded valid files | Implemented in downloader.py lines 218-237 |
| OUT-04 | System detects and handles corrupted existing files | Implemented with `is_pdf_valid()` and `--delete-corrupted` flag |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python os.path | built-in | Path manipulation | Universal, battle-tested |
| pathlib | built-in | Modern path handling | Recommended for new code |
| PyMuPDF (fitz) | latest | PDF validation | Already in use, robust |

### Existing Code Patterns
The project already uses:
- `os.path.join()` for path construction
- `os.makedirs(exist_ok=True)` for directory creation
- `re.sub()` for filename sanitization
- `fitz.open()` for PDF validation

### Alternatives Considered
| Approach | Instead of | Tradeoff |
|----------|------------|----------|
| pathlib.Path | os.path | More object-oriented, cross-platform; existing code uses os.path |
| pypdf | fitz | Different API; fitz already integrated |

## Architecture Patterns

### Recommended Project Structure
No new modules needed. Work centers on existing files:
```
scihub_download/
├── cli.py         # Already has --output, --format flags
├── downloader.py  # Contains clean_filename(), is_pdf_valid()
```

### Pattern 1: Filename Generation with Pattern Selection
**What:** `clean_filename()` function needs to support multiple patterns
**When to use:** When generating output filename for downloaded PDF
**Example:**
```python
def clean_filename(identifier: str, pattern: str = "pmid") -> str:
    """Create filename based on pattern choice.

    Args:
        identifier: PMID or DOI to use in filename
        pattern: "pmid", "doi", or "original"
    """
    if pattern == "original" and identifier != "original":
        # Use identifier as provided (for metadata-based names)
        return identifier
    # Sanitize and append .pdf
    return re.sub(r'[\\/*?:"<>|]', '_', identifier) + ".pdf"
```

### Pattern 2: File Pre-check Before Download
**What:** Check existing files before attempting download
**When to use:** Always - avoids redundant downloads
**Example:** (already in downloader.py lines 218-237)
```python
for _, row in df.iterrows():
    filepath = os.path.join(save_dir, clean_filename(row['PMID']))
    if os.path.exists(filepath):
        if not is_pdf_valid(filepath):
            # Corrupted - re-download
            df_to_download.append(row)
        else:
            # Valid - skip
            logging.info(f"[EXISTS] {row['PMID']}")
```

### Anti-Patterns to Avoid
- **Hardcoded filename pattern:** Don't always use PMID - respect user's `--format` choice
- **Missing directory creation:** Always use `os.makedirs(exist_ok=True)` before writing
- **Insufficient filename sanitization:** Remove all invalid characters, not just some

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF validation | Custom parser | PyMuPDF (fitz) | Already integrated, handles edge cases |
| Path joining | String concatenation | os.path.join() | Handles OS differences |
| Invalid filename chars | Partial removal | Full regex replacement | Covers all OS-incompatible characters |

## Common Pitfalls

### Pitfall 1: CLI Arguments Not Connected to Logic
**What goes wrong:** User sets `--format doi` but downloader ignores it
**Why it happens:** CLI parses flag but never passes value to download functions
**How to avoid:** Pass `args.format` through the call chain to `clean_filename()`
**Warning signs:** Any new CLI flag that doesn't affect download behavior

### Pitfall 2: Filename Pattern Mismatch
**What goes wrong:** Pre-check uses PMID pattern but download uses DOI pattern
**Why it happens:** Inconsistent pattern usage between check and save
**How to avoid:** Use same pattern function for both operations, centralize pattern choice
**Warning signs:** Files being re-downloaded unexpectedly or not found when they exist

### Pitfall 3: Race Condition in Parallel Downloads
**What goes wrong:** Two threads compute same filename, one overwrites the other
**Why it happens:** No file locking for concurrent writes to same path
**How to avoid:** Check for file existence atomically or use thread-safe naming
**Warning signs:** Files with partial content, corrupted PDFs

## Code Examples

### Existing: PDF Validation (downloader.py:55-65)
```python
def is_pdf_valid(filepath: str) -> bool:
    """检查 PDF 是否有效"""
    if not os.path.exists(filepath):
        return False
    try:
        doc = fitz.open(filepath)
        valid = doc.page_count > 0
        doc.close()
        return valid
    except Exception:
        return False
```

### Existing: Filename Sanitization (downloader.py:51-53)
```python
def clean_filename(pmid: str) -> str:
    """用 PMID 创建合法文件名"""
    return re.sub(r'[\\/*?:"<>|]', '_', pmid) + ".pdf"
```

### Gap: CLI not passing format to downloader
```python
# cli.py main() needs to pass args.format to download functions
# Currently: print(f"Format: {args.format}") - just printing, not using
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| os.path only | pathlib available | Python 3.4+ | Either works, no migration needed |
| Manual PDF size check | fitz validation | Phase 3 | More robust corruption detection |

**Deprecated/outdated:**
- None specific to this phase

## Open Questions

1. **Custom filename pattern implementation**
   - What we know: CLI has `--format` with choices ["pmid", "doi", "original"]
   - What's unclear: What does "original" mean - original DOI string? PDF title metadata?
   - Recommendation: Use "original" to preserve DOI as-is (simplest interpretation)

2. **Thread safety for file operations**
   - What we know: Parallel downloads use ThreadPoolExecutor
   - What's unclear: Whether file overwrites could occur with same PMID
   - Recommendation: Each PMID is unique, so collision unlikely; add assert to verify

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | pytest.ini (if exists) or default |
| Quick run command | `pytest tests/ -x` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| OUT-01 | Output directory specified | unit/integration | `pytest tests/test_cli.py -k output -x` | No - add to test_cli.py |
| OUT-02 | Filename pattern works | unit | `pytest tests/test_downloader.py -k filename -x` | No - add to test_downloader.py |
| OUT-03 | Skip valid existing files | integration | `pytest tests/test_integration.py -k skip -x` | No - add to test_integration.py |
| OUT-04 | Detect corrupted files | integration | `pytest tests/test_integration.py -k corrupted -x` | No - add to test_integration.py |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x` (fast)
- **Per wave merge:** `pytest tests/ -v` (full)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_downloader.py` — covers OUT-02, OUT-04
- [ ] `tests/test_integration.py` — add tests for OUT-03, OUT-04
- [ ] `tests/test_cli.py` — add test for OUT-01

Existing test files:
- tests/test_cli.py exists but needs new tests for file output
- tests/test_integration.py exists but needs new test cases

## Sources

### Primary (HIGH confidence)
- Existing codebase analysis (cli.py, downloader.py)
- PyMuPDF/fiTz documentation

### Secondary (MEDIUM confidence)
- Python os.path documentation
- Python pathlib documentation

### Tertiary (LOW confidence)
- N/A (well-understood domain)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - existing implementation uses standard Python libraries
- Architecture: HIGH - clear patterns from existing code
- Pitfalls: HIGH - gaps identified through code analysis

**Research date:** 2026-03-19
**Valid until:** 90 days (stable Python stdlib)
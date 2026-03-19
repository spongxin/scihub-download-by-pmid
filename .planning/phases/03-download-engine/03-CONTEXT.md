# Phase 3: Download Engine - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Multi-threaded PDF downloads with progress display, validation, and error handling. Users can reliably download PDFs with rich progress feedback and smart retry logic. Depends on Phase 2 (Source Management).

</domain>

<decisions>
## Implementation Decisions

### Retry Strategy
- Try all available sources once for each DOI
- If all sources fail, the DOI is marked as failed
- No explicit retry counting per DOI (simpler approach)

### Progress Display
- Single aggregate progress bar (tqdm)
- Shows: overall file count progress
- Minimal info below bar - count only
- Good for both interactive use and scripts/CI

### Error Handling
- Skip 404 errors immediately (not found = permanent failure)
- Retry network errors (timeouts, connection issues) by trying next source
- Log error type and source URL for debugging
- Failure categories: 404 (not found), network error, validation failure

### Worker Configuration
- Default: 5 worker threads (good balance of speed and stability)
- Maximum: 20 workers (prevent accidental system overwhelm)
- --workers flag already implemented in Phase 1

### Claude's Discretion
- Exact timeout values for downloads vs source checks
- Progress bar styling details
- How to handle validation failures (corrupted PDF after download)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Requirements
- `.planning/REQUIREMENTS.md` — DL-01 through DL-06 requirements
- `.planning/ROADMAP.md` — Phase 3 goal and success criteria

### Existing Code
- `scihub_download/downloader.py` — Current download implementation (to be enhanced)
- `scihub_download/source_manager.py` — Source management from Phase 2

No external specs — requirements fully captured in decisions above

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tqdm` progress bar — already in use, continue with single aggregate bar
- `fitz` (PyMuPDF) — already used for PDF validation
- `ThreadPoolExecutor` — already implemented

### Established Patterns
- ThreadPoolExecutor with max_workers parameter
- Source iteration loop for failover
- Logging with PMID/DOI context

### Integration Points
- Connects to SourceManager for source list
- Uses input_parser to get DOI list
- Output goes to file system (handled in Phase 4)
- Failed downloads tracked for reporting (Phase 5)

</code_context>

<specifics>
## Specific Ideas

- Keep the existing tqdm approach - it's already working well
- 5 workers default aligns with current code
- Error logging should help debug source issues

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-download-engine*
*Context gathered: 2026-03-19*
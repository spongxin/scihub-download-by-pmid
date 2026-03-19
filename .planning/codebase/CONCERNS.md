# Concerns: SciHub Download by PMID

## Technical Debt

### 1. No Test Coverage
- **Impact**: High
- **Description**: No unit or integration tests exist
- **Risk**: Changes may break functionality undetected

### 2. Hardcoded Sci-Hub URLs
- **Impact**: Medium
- **Description**: Mirror URLs are hardcoded in the script
- **Risk**: URLs may become stale; requires code changes to update

### 3. No Configuration File
- **Impact**: Low
- **Description**: All configuration via CLI args or constants
- **Risk**: Complex CLI invocations are error-prone

## Known Limitations

| Limitation | Impact |
|------------|--------|
| Single-file architecture | Harder to maintain as features grow |
| No async I/O | Limited concurrency control |
| Basic PDF validation | Only checks page count, not content |
| No rate limiting | May trigger server-side throttling |

## Security Considerations

- **No input sanitization** beyond filename cleaning
- **No HTTPS verification** configuration (uses default requests verification)
- **No credential storage** (no auth required)

## Performance Considerations

- **Thread pool**: Fixed at 5 workers (configurable)
- **No connection pooling** beyond session reuse
- **No retry with backoff** (immediate fallback only)

## Fragile Areas

1. **HTML parsing regex**: Relies on specific iframe/embed patterns from Sci-Hub
2. **DOI URL construction**: Assumes consistent URL patterns across mirrors
3. **File existence checks**: Race conditions possible in parallel mode

## Recommendations

| Priority | Action |
|----------|--------|
| High | Add unit tests for core functions |
| Medium | Extract URLs to config file |
| Low | Consider async/await for better concurrency |

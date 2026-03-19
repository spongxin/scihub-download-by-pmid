# Testing: SciHub Download by PMID

## Current State

**No tests present.**

The codebase has no unit tests, integration tests, or test infrastructure.

## Testing Gaps

| Area | Risk |
|------|------|
| Download logic | No verification of PDF extraction |
| URL parsing | No tests for iframe regex patterns |
| File validation | No tests for PDF validation |
| Error handling | No tests for failure scenarios |
| CLI arguments | No tests for argument parsing |

## Recommendations

If tests were to be added:

1. **Unit tests** (`tests/test_*.py`):
   - `clean_filename()` - Test sanitization logic
   - `is_pdf_valid()` - Test with valid/invalid PDFs
   - URL extraction regex patterns

2. **Integration tests**:
   - Mock HTTP responses for download logic
   - Test with sample CSV files

3. **Test framework**: pytest (recommended)

## Test Data

No test fixtures or sample data present.

## Coverage

- **Current**: 0%
- **Recommended target**: 70%+ for critical paths

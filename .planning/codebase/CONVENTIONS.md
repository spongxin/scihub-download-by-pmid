# Conventions: SciHub Download by PMID

## Code Style

- **Python style**: PEP 8 conventions
- **Indentation**: 4 spaces
- **String quotes**: Double quotes
- **Line length**: ~120 characters (observed in main function)

## Naming Patterns

| Element | Convention | Example |
|---------|------------|---------|
| Functions | snake_case | `download_worker`, `clean_filename` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_SCI_HUB_SOURCES` |
| Variables | snake_case | `pdf_url`, `filepath` |
| Private helpers | Leading underscore (not used) | N/A |

## Error Handling

- **Network errors**: Caught and logged, returns False
- **File errors**: Caught and logged
- **Invalid data**: Logged and skipped

## Logging

- **Level**: INFO and above
- **Format**: `%(asctime)s - %(levelname)s - %(message)s`
- **Output**: Both file and console

## Patterns Used

- **Session reuse**: Single `requests.Session` for all HTTP calls
- **Context managers**: `with` statements for file and response handling
- **Type hints**: Present on function signatures
- **Docstrings**: Google-style for functions

## Not Present (Potential Improvements)

- No unit tests
- No configuration file (all CLI args or hardcoded)
- No async/await (uses threading instead)
- No structured logging (json/formatted)

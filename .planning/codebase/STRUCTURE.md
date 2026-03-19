# Structure: SciHub Download by PMID

## Directory Layout

```
scihub-download-by-pmid/
├── scihub_download_chenwei.py    # Main script (188 lines)
├── .planning/
│   └── codebase/                  # Codebase documentation
│       ├── STACK.md
│       ├── ARCHITECTURE.md
│       ├── STRUCTURE.md
│       ├── CONVENTIONS.md
│       ├── TESTING.md
│       ├── INTEGRATIONS.md
│       └── CONCERNS.md
└── .git/                          # Git repository
```

## Key Locations

| Location | Purpose |
|----------|---------|
| `scihub_download_chenwei.py` | All application logic |
| `.planning/codebase/` | Documentation of codebase state |

## File Organization

**Single-file application** - All functionality contained in one Python script organized by:

1. Imports and type hints (lines 1-12)
2. Default configuration (lines 14-26)
3. Logging setup (lines 29-37)
4. Utility functions (lines 40-71)
5. Download worker (lines 74-104)
6. Main function (lines 107-188)

## Naming Conventions

- **Python files**: snake_case
- **Functions**: snake_case with verb prefix (e.g., `download_worker`, `is_pdf_valid`)
- **Constants**: UPPER_SNAKE_CASE
- **Variables**: snake_case

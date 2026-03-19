# UAT: Phase 1 - Foundation

**Created:** 2026-03-19
**Phase:** 01-foundation
**Status:** In Progress

## Testable Deliverables

| # | Feature | Test Command | Expected Result |
|---|---------|--------------|-----------------|
| 1 | Module help | `python -m scihub_download --help` | Shows help with all options |
| 2 | CLI help | `scihub-download --help` | Shows help with all options |
| 3 | CSV input | `scihub-download --file data.csv` | Loads IDs from CSV |
| 4 | TXT input | `scihub-download --file data.txt` | Loads IDs from TXT |
| 5 | XLSX input | `scihub-download --file data.xlsx` | Loads IDs from Excel |
| 6 | Single PMID | `scihub-download --id 12345` | Processes single PMID |
| 7 | Single DOI | `scihub-download --id 10.1234/test` | Processes single DOI |
| 8 | Output flag | `--output /path/to/dir` | Sets output directory |
| 9 | Workers flag | `--workers 4` | Sets thread count |
| 10 | Format flag | `--format pmid` | Sets filename pattern |
| 11 | Verbose flag | `-v` | Increases verbosity |
| 12 | Quiet flag | `-q` | Decreases verbosity |

## Results

| # | Status | Notes |
|---|--------|-------|
| 1 | ✅ PASS | Shows all CLI options |
| 2 | ✅ PASS | Shows all CLI options |
| 3 | ✅ PASS | Loaded 1 record from CSV |
| 4 | ✅ PASS | Loaded 2 records from TXT |
| 5 | ✅ PASS | Loaded 1 record from XLSX |
| 6 | ✅ PASS | Processed single PMID |
| 7 | ✅ PASS | Processed single DOI |
| 8 | ✅ PASS | Output set to /tmp/mypdfs |
| 9 | ✅ PASS | Workers set to 4 |
| 10 | ✅ PASS | Format set to doi |
| 11 | ✅ PASS | Verbose enabled |
| 12 | ✅ PASS | Quiet mode enabled |

## Issues Found

None.
---
phase: 02-source-management
plan: "01"
subsystem: source-management
tags:
  - source-discovery
  - health-checking
  - caching
  - failover
dependency_graph:
  requires:
    - phase-01-foundation
  provides:
    - SRC-01
    - SRC-02
    - SRC-03
    - SRC-04
  affects:
    - scihub_download/downloader.py
    - scihub_download/cli.py
tech_stack:
  added:
    - beautifulsoup4
    - lxml
  patterns:
    - ThreadPoolExecutor for parallel health checks
    - JSON file cache with TTL
    - Dataclass for structured source status
key_files:
  created:
    - scihub_download/source_manager.py
    - tests/test_source_manager.py
  modified:
    - scihub_download/downloader.py
    - requirements.txt
decisions:
  - "SourceManager creates its own session to avoid coupling with downloader's session"
  - "Cache TTL set to 24 hours to balance freshness with performance"
  - "Parallel source testing with 5 workers to avoid overwhelming sources"
  - "HEAD requests for health checks (lighter than GET)"
metrics:
  duration: ""
  completed_date: "2026-03-19"
  tasks_completed: 4
  tests_passed: 16
---

# Phase 02 Plan 01: Source Management Summary

Dynamic SciHub source discovery, health checking, ranking, and automatic failover implemented.

## Completed Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create source_manager.py module | 46f67f3 | scihub_download/source_manager.py |
| 2 | Add beautifulsoup4 to requirements.txt | 1fd877b | requirements.txt |
| 3 | Create tests for source_manager | 0c85c3c | tests/test_source_manager.py |
| 4 | Integrate source manager with downloader | fa75e09 | scihub_download/downloader.py |

## One-Liner

Dynamic SciHub source discovery, health checking, ranking with 24h cache, and automatic failover.

## Requirements Addressed

- **SRC-01:** scrape_sources() fetches from sci-hub.pub
- **SRC-02:** test_source() uses HEAD requests
- **SRC-03:** rank_sources() sorts by success rate + response time
- **SRC-04:** download_worker continues to next source on failure

## Key Features Implemented

1. **Source Discovery:** Scrapes sci-hub.pub for available sources, falls back to defaults
2. **Health Checking:** Parallel HEAD requests with timeout handling
3. **Ranking:** Sorts by success rate (desc), then response time (asc)
4. **Caching:** JSON cache with 24-hour TTL, auto-refresh on invalid cache
5. **Failover:** download_worker logs "trying next source..." on each failure

## Test Results

All 16 tests pass:
- SourceStatus dataclass tests (4)
- Default configuration tests (3)
- Scrape sources tests (2)
- Test source tests (2)
- Rank sources tests (2)
- Cache tests (2)
- Convenience function tests (1)

## Self-Check: PASSED

All verification criteria met:
- source_manager.py exists with all required methods
- requirements.txt contains beautifulsoup4
- test_source_manager.py exists with all required tests
- downloader.py imports SourceManager and has failover logging
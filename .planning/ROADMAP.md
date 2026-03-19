# Roadmap: SciHub Downloader CLI

**Created:** 2026-03-19
**Core Value:** Reliably download PDFs from Sci-Hub with minimal user intervention
**Granularity:** Coarse (3-5 phases)

## Phases

- [ ] **Phase 1: Foundation** - CLI interface and multi-format input support
- [x] **Phase 2: Source Management** - Dynamic SciHub source discovery and switching (completed 2026-03-19)
- [ ] **Phase 3: Download Engine** - Multi-threaded downloads with validation and retry
- [ ] **Phase 4: File Output** - Output directory and filename control
- [ ] **Phase 5: Reporting** - Download reports and terminal summaries

## Phase Details

### Phase 1: Foundation
**Goal:** Users can run the tool with various inputs and configure options
**Depends on:** Nothing (first phase)
**Requirements:** INPUT-01, INPUT-02, INPUT-03, INPUT-04, CLI-01, CLI-02, CLI-03, CLI-04, CLI-05, CLI-06
**Success Criteria** (what must be TRUE):
1. User can run `scihub-download --help` and see all documented options
2. User can provide input via CSV file with PMID/DOI columns
3. User can provide input via TXT file with one ID per line
4. User can provide input via Excel file (.xlsx)
5. User can specify a single PMID/DOI via command line argument
**Plans:** 4 plans in 3 waves

Plans:
- [x] 01-PLAN-00.md - Test infrastructure setup (pytest, fixtures, test stubs)
- [x] 01-PLAN-01.md - Input parser module (CSV, TXT, Excel, single ID)
- [x] 01-PLAN-02.md - CLI argument parser (all flags CLI-01 to CLI-06)
- [x] 01-PLAN-03.md - Integration and entry point

### Phase 2: Source Management
**Goal:** System reliably discovers and manages working SciHub sources
**Depends on:** Phase 1
**Requirements:** SRC-01, SRC-02, SRC-03, SRC-04
**Success Criteria** (what must be TRUE):
1. System automatically fetches available sources from sci-hub.pub
2. System tests each source by attempting actual download
3. System ranks sources by response time and success rate
4. System automatically switches to next source when current fails
**Plans:** 1/1 plans complete

Plans:
- [x] 02-01-PLAN.md - Source Manager (scraping, testing, ranking, failover)

### Phase 3: Download Engine
**Goal:** Users can reliably download PDFs with rich progress feedback
**Depends on:** Phase 2
**Requirements:** DL-01, DL-02, DL-03, DL-04, DL-05, DL-06
**Success Criteria** (what must be TRUE):
1. User sees rich progress bar during parallel downloads
2. User can configure number of worker threads via --workers flag
3. System validates downloaded PDFs are not corrupted
4. System retries network errors up to 3 times but skips 404s immediately
**Plans:** 1/1 plans

Plans:
- [x] 03-01-PLAN.md - Error classification and smart retry logic

### Phase 4: File Output
**Goal:** Users have control over where and how files are saved
**Depends on:** Phase 3
**Requirements:** OUT-01, OUT-02, OUT-03, OUT-04
**Success Criteria** (what must be TRUE):
1. User can specify output directory via --output flag
2. User can choose filename pattern (PMID, DOI, or custom)
3. System skips already downloaded valid files (no redownload)
4. System detects corrupted existing files and re-downloads them
**Plans:** 1/1 plans

Plans:
- [x] 04-01-PLAN.md - Connect CLI --format to downloader, implement filename patterns

### Phase 5: Reporting
**Goal:** Users have clear visibility into download results
**Depends on:** Phase 4
**Requirements:** RPT-01, RPT-02, RPT-03, RPT-04
**Success Criteria** (what must be TRUE):
1. User sees terminal summary with success/failure counts after completion
2. User receives CSV file listing all failed downloads
3. User sees detailed report including total time, success rate, and per-source statistics
**Plans:** TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 4/4 | Complete | 2026-03-19 |
| 2. Source Management | 1/1 | Complete | 2026-03-19 |
| 3. Download Engine | 1/1 | Complete | 2026-03-19 |
| 4. File Output | 1/1 | Complete | 2026-03-19 |
| 5. Reporting | 0/1 | Not started | - |

## Coverage

| Category | Requirements | Phase |
|----------|--------------|-------|
| Input Processing | INPUT-01, INPUT-02, INPUT-03, INPUT-04 | Phase 1 |
| CLI Interface | CLI-01, CLI-02, CLI-03, CLI-04, CLI-05, CLI-06 | Phase 1 |
| Source Management | SRC-01, SRC-02, SRC-03, SRC-04 | Phase 2 |
| Download Engine | DL-01, DL-02, DL-03, DL-04, DL-05, DL-06 | Phase 3 |
| File Output | OUT-01, OUT-02, OUT-03, OUT-04 | Phase 4 |
| Reporting | RPT-01, RPT-02, RPT-03, RPT-04 | Phase 5 |

**Total:** 28/28 requirements mapped (100%)

---
*Roadmap created: 2026-03-19*
*Phase 1 planned: 2026-03-19*
*Phase 2 planned: 2026-03-19*
*Phase 2 executed: 2026-03-19*
*Phase 3 planned: 2026-03-19*
*Phase 3 Plan 01 executed: 2026-03-19*
*Phase 4 planned: 2026-03-19*
*Phase 4 Plan 01 executed: 2026-03-19*
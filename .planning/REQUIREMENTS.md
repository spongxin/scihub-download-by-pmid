# Requirements: SciHub Downloader CLI

**Defined:** 2026-03-19
**Core Value:** Reliably download PDFs from Sci-Hub with minimal user intervention

## v1 Requirements

### Input Processing

- [ ] **INPUT-01**: User can provide input file in CSV format with PMID/DOI columns
- [ ] **INPUT-02**: User can provide input file in TXT format (one PMID/DOI per line)
- [ ] **INPUT-03**: User can provide input file in Excel format (.xlsx)
- [ ] **INPUT-04**: User can specify PMID or DOI directly via command line argument

### Source Management

- [ ] **SRC-01**: System automatically fetches available SciHub sources from sci-hub.pub
- [ ] **SRC-02**: System tests each source by attempting actual download
- [ ] **SRC-03**: System ranks sources by response time and success rate
- [ ] **SRC-04**: System automatically switches to next source when current fails

### Download Engine

- [ ] **DL-01**: System downloads PDFs using multi-threading
- [ ] **DL-02**: System displays rich progress bar during downloads
- [ ] **DL-03**: System validates downloaded PDFs are not corrupted
- [ ] **DL-04**: System implements smart retry based on error type
- [ ] **DL-05**: System retries network errors up to 3 times
- [ ] **DL-06**: System does not retry 404/not found errors

### File Output

- [ ] **OUT-01**: User can specify output directory for PDFs
- [ ] **OUT-02**: User can choose filename pattern (PMID, DOI, or custom)
- [ ] **OUT-03**: System skips already downloaded valid files
- [ ] **OUT-04**: System detects and handles corrupted existing files

### Reporting

- [ ] **RPT-01**: System generates CSV file of failed downloads
- [ ] **RPT-02**: System displays terminal summary with success/failure counts
- [ ] **RPT-03**: System generates download report with statistics
- [ ] **RPT-04**: Report includes total time, success rate, per-source stats

### CLI Interface

- [ ] **CLI-01**: CLI supports --verbose/-v flag for detailed output
- [ ] **CLI-02**: CLI supports --quiet/-q flag for minimal output
- [ ] **CLI-03**: CLI supports --workers/-w flag for thread count
- [ ] **CLI-04**: CLI supports --output/-o flag for output directory
- [ ] **CLI-05**: CLI supports --format/-f flag for filename pattern
- [ ] **CLI-06**: CLI displays help message with all options documented

## v2 Requirements

### Advanced Features

- **ADV-01**: User can resume interrupted download sessions
- **ADV-02**: System supports proxy configuration
- **ADV-03**: System caches source availability results

## Out of Scope

| Feature | Reason |
|---------|--------|
| Metadata fetching | User confirmed not needed |
| GUI interface | CLI only for v1 |
| OAuth/authentication | Sci-Hub requires no auth |
| Async/await | Threading is sufficient |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INPUT-01 | Phase 1 | Pending |
| INPUT-02 | Phase 1 | Pending |
| INPUT-03 | Phase 1 | Pending |
| INPUT-04 | Phase 1 | Pending |
| SRC-01 | Phase 2 | Pending |
| SRC-02 | Phase 2 | Pending |
| SRC-03 | Phase 2 | Pending |
| SRC-04 | Phase 2 | Pending |
| DL-01 | Phase 3 | Pending |
| DL-02 | Phase 3 | Pending |
| DL-03 | Phase 3 | Pending |
| DL-04 | Phase 3 | Pending |
| DL-05 | Phase 3 | Pending |
| DL-06 | Phase 3 | Pending |
| OUT-01 | Phase 4 | Pending |
| OUT-02 | Phase 4 | Pending |
| OUT-03 | Phase 4 | Pending |
| OUT-04 | Phase 4 | Pending |
| RPT-01 | Phase 5 | Pending |
| RPT-02 | Phase 5 | Pending |
| RPT-03 | Phase 5 | Pending |
| RPT-04 | Phase 5 | Pending |
| CLI-01 | Phase 1 | Pending |
| CLI-02 | Phase 1 | Pending |
| CLI-03 | Phase 1 | Pending |
| CLI-04 | Phase 1 | Pending |
| CLI-05 | Phase 1 | Pending |
| CLI-06 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 28
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-19*
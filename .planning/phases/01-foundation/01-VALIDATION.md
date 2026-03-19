---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pytest tests/ -v` |
| **Full suite command** | `pytest tests/ -v --cov=scihub_download` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -v`
- **After every plan wave:** Run `pytest tests/ -v --cov=scihub_download`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | INPUT-01 | unit | `pytest tests/test_input_parser.py::test_parse_csv -v` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | INPUT-02 | unit | `pytest tests/test_input_parser.py::test_parse_txt -v` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | INPUT-03 | unit | `pytest tests/test_input_parser.py::test_parse_xlsx -v` | ❌ W0 | ⬜ pending |
| 01-01-04 | 01 | 1 | INPUT-04 | unit | `pytest tests/test_input_parser.py::test_parse_single_id -v` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | CLI-01 | unit | `pytest tests/test_cli.py::test_verbose_flag -v` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 1 | CLI-02 | unit | `pytest tests/test_cli.py::test_quiet_flag -v` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 1 | CLI-03 | unit | `pytest tests/test_cli.py::test_workers_flag -v` | ❌ W0 | ⬜ pending |
| 01-02-04 | 02 | 1 | CLI-04 | unit | `pytest tests/test_cli.py::test_output_flag -v` | ❌ W0 | ⬜ pending |
| 01-02-05 | 02 | 1 | CLI-05 | unit | `pytest tests/test_cli.py::test_format_flag -v` | ❌ W0 | ⬜ pending |
| 01-02-06 | 02 | 1 | CLI-06 | unit | `pytest tests/test_cli.py::test_help_message -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — test package initialization
- [ ] `tests/conftest.py` — shared fixtures (sample CSV, TXT, XLSX files)
- [ ] `tests/test_cli.py` — CLI argument parsing tests (covers CLI-01 to CLI-06)
- [ ] `tests/test_input_parser.py` — input parsing tests (covers INPUT-01 to INPUT-04)
- [ ] `pip install pytest pytest-cov` — test framework installation
- [ ] `pip install openpyxl` — Excel support for pandas

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Help message formatting | CLI-06 | Terminal output varies | Run `scihub-download --help` and verify all options visible |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
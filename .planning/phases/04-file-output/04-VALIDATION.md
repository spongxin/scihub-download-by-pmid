---
phase: 4
slug: file-output
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pytest.ini (if exists) or default |
| **Quick run command** | `pytest tests/ -x` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | OUT-02 | unit | `pytest tests/test_downloader.py -k clean_filename -x` | No | ⬜ pending |
| 04-01-02 | 01 | 1 | OUT-02 | unit | `pytest tests/test_cli.py -k format -x` | No | ⬜ pending |
| 04-01-03 | 01 | 1 | OUT-03, OUT-04 | integration | `pytest tests/test_integration.py -k skip -x` | Yes | ⬜ pending |
| 04-01-04 | 01 | 1 | OUT-01 to OUT-04 | unit | `pytest tests/test_downloader.py -x` | No | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_downloader.py` — add tests for clean_filename patterns (OUT-02, OUT-04)
- [ ] `tests/test_integration.py` — add tests for skip valid files and corrupted detection (OUT-03, OUT-04)
- [ ] `tests/test_cli.py` — add test for --format flag (OUT-02)

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Verify --output flag works end-to-end | OUT-01 | Requires actual file download | Run with --output /tmp/test && verify file created |
| Verify corrupted file re-download | OUT-04 | Requires file corruption | Corrupt PDF manually, run again, verify re-download |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
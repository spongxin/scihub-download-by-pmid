# Phase 2 Context: Source Management

**Phase:** 02-source-management
**Created:** 2026-03-19

## Decisions Made

### 1. Source Discovery Strategy
- **Selected:** 爬取 sci-hub.pub
- **Implementation:** Use BeautifulSoup to scrape available Sci-Hub mirrors from sci-hub.pub
- **Fallback:** Use hardcoded DEFAULT_SCI_HUB_SOURCES if scraping fails

### 2. Source Health Check
- **Selected:** HEAD 请求
- **Implementation:** Send HTTP HEAD requests to test source availability
- **Metrics:** Response time, HTTP status code

### 3. Source Ranking
- **Selected:** 成功率优先
- **Implementation:** Track historical success rate per source
- **Tie-breaker:** Use response time as secondary sort key

### 4. Source Caching
- **Selected:** 24小时缓存
- **Implementation:** Cache source status in local JSON file
- **Cache location:** ~/.scihub_download/sources_cache.json

## Phase 2 Requirements

- [ ] **SRC-01**: Fetch sources from sci-hub.pub
- [ ] **SRC-02**: Test each source by HEAD request
- [ ] **SRC-03**: Rank by success rate (primary) + response time (secondary)
- [ ] **SRC-04**: Auto-switch when current fails

## Code Integration Points

### Existing Code
- `scihub_download/downloader.py`: Contains DEFAULT_SCI_HUB_SOURCES (lines 14-21)
- `download_worker()`: Iterates through sources in order (line 81)

### New Module Needed
- `scihub_download/source_manager.py`: Source discovery, testing, and ranking

### Integration
- Source manager should be initialized at CLI startup
- Pass source list to download_worker()
- Auto-refresh if cache is expired (>24h)

## Technical Notes

- Use `requests` for HTTP (already a dependency)
- Use `beautifulsoup4` for scraping (need to add to dependencies)
- Cache format: JSON with source URL, success_count, total_attempts, avg_response_time, last_checked
- On first run: scrape sources → test all → rank → use top N

## Dependencies to Add

```
beautifulsoup4>=4.9.0
```

---

*Context captured from discuss-phase: 2026-03-19*
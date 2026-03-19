# Integrations: SciHub Download by PMID

## External Services

### Sci-Hub Mirrors

| URL | Status |
|-----|--------|
| https://sci-hub.se | Primary |
| https://sci-hub.ru | Fallback |
| https://sci-hub.red | Fallback |
| https://sci-hub.ee | Fallback |
| https://sci-hub.vg | Fallback |
| https://sci-hub.shop | Fallback |

**Usage pattern**: Multiple mirrors tried in sequence until download succeeds.

### HTTP Integration

- **Library**: `requests`
- **Session**: Persistent session with custom User-Agent
- **Timeouts**: 90s for requests, 120s for downloads
- **Retry strategy**: Manual retry via mirror fallback (no auto-retry)

## File System

### Input
- **CSV file**: Must contain `PMID` and `DOI` columns

### Output
- **PDF files**: Named by PMID (`{PMID}.pdf`)
- **Failed records CSV**: Optional, tracks failed downloads
- **Log file**: Default `download_log.txt`

## No Other Integrations

- No database
- No authentication providers
- No webhooks
- No external APIs beyond Sci-Hub

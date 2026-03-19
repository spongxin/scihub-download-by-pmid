"""SciHub source management: discovery, health checking, ranking, and caching."""

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class SourceStatus:
    """Status information for a Sci-Hub source."""
    url: str
    success_count: int = 0
    total_attempts: int = 0
    avg_response_time_ms: float = 999999.0
    last_checked: str = ""

    @property
    def available(self) -> bool:
        """Whether the source is available (has success history)."""
        return self.success_count > 0

    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        if self.total_attempts == 0:
            return 0.0
        return (self.success_count / self.total_attempts) * 100


class SourceManager:
    """Manages Sci-Hub source discovery, health checking, and ranking."""

    DEFAULT_SCI_HUB_SOURCES = [
        "https://sci-hub.se",
        "https://sci-hub.ru",
        "https://sci-hub.red",
        "https://sci-hub.ee",
        "https://sci-hub.vg",
        "https://sci-hub.shop",
    ]

    CACHE_FILE = os.path.expanduser("~/.scihub_download/sources_cache.json")
    CACHE_TTL_HOURS = 24
    SCRAPE_URL = "https://sci-hub.pub/"
    SCRAPE_TIMEOUT = 10
    TEST_TIMEOUT = 15
    MAX_WORKERS = 5

    def __init__(self, session: Optional[requests.Session] = None):
        """Initialize SourceManager with optional custom session."""
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    # -------------------- Cache Methods --------------------

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        cache_path = Path(self.CACHE_FILE)
        cache_path.parent.mkdir(parents=True, exist_ok=True)

    def load_cache(self) -> Dict[str, SourceStatus]:
        """Load source cache from JSON file."""
        if not os.path.exists(self.CACHE_FILE):
            return {}
        try:
            with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {url: SourceStatus(**status) for url, status in data.items()}
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to load cache: {e}")
            return {}

    def save_cache(self, sources: List[SourceStatus]) -> None:
        """Save source cache to JSON file."""
        self._ensure_cache_dir()
        data = {s.url: asdict(s) for s in sources}
        with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Cached {len(sources)} sources to {self.CACHE_FILE}")

    def is_cache_valid(self) -> bool:
        """Check if cache exists and is less than CACHE_TTL_HOURS old."""
        if not os.path.exists(self.CACHE_FILE):
            return False
        try:
            mtime = os.path.getmtime(self.CACHE_FILE)
            age_hours = (time.time() - mtime) / 3600
            return age_hours < self.CACHE_TTL_HOURS
        except OSError:
            return False

    # -------------------- Source Discovery --------------------

    def scrape_sources(self) -> List[str]:
        """Scrape Sci-Hub sources from sci-hub.pub."""
        try:
            response = self.session.get(self.SCRAPE_URL, timeout=self.SCRAPE_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            # Find all links containing sci-hub.* domains
            sources = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'sci-hub.' in href:
                    # Extract domain
                    import re
                    match = re.search(r'https?://(sci-hub\.[a-z]+)', href)
                    if match:
                        sources.add(f"https://{match.group(1)}")

            if sources:
                logger.info(f"Found {len(sources)} sources from {self.SCRAPE_URL}")
                return sorted(sources)

            logger.warning("No sources found from scrape, using defaults")
        except Exception as e:
            logger.warning(f"Failed to scrape sources: {e}")

        return self.DEFAULT_SCI_HUB_SOURCES.copy()

    # -------------------- Health Checking --------------------

    def test_source(self, source_url: str) -> SourceStatus:
        """Test a single source with HEAD request."""
        start_time = time.time()
        status = SourceStatus(url=source_url, last_checked=datetime.utcnow().isoformat())

        try:
            response = self.session.head(source_url, timeout=self.TEST_TIMEOUT)
            response.raise_for_status()
            status.success_count = 1
            status.total_attempts = 1
            status.avg_response_time_ms = (time.time() - start_time) * 1000
            logger.debug(f"Source {source_url} OK: {response.status_code}")
        except requests.exceptions.Timeout:
            status.total_attempts = 1
            logger.debug(f"Source {source_url} timeout")
        except requests.exceptions.RequestException as e:
            status.total_attempts = 1
            logger.debug(f"Source {source_url} failed: {e}")

        return status

    def test_all_sources(self, sources: List[str]) -> List[SourceStatus]:
        """Test all sources in parallel."""
        results = []
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = {executor.submit(self.test_source, url): url for url in sources}
            for future in as_completed(futures):
                results.append(future.result())
        return results

    # -------------------- Ranking --------------------

    def rank_sources(self, sources: List[SourceStatus]) -> List[SourceStatus]:
        """Rank sources by success rate (desc), then response time (asc)."""
        return sorted(
            sources,
            key=lambda s: (-s.success_rate, s.avg_response_time_ms)
        )

    # -------------------- Main API --------------------

    def get_best_sources(self, n: int = 3, force_refresh: bool = False) -> List[str]:
        """Get the n best available sources.

        Args:
            n: Number of sources to return
            force_refresh: Force cache refresh

        Returns:
            List of URLs for the best sources
        """
        # Check cache
        if not force_refresh and self.is_cache_valid():
            logger.info("Loading sources from cache")
            cached = self.load_cache()
            if cached:
                # Test cached sources to verify they're still working
                test_results = self.test_all_sources(list(cached.keys()))
                ranked = self.rank_sources(test_results)
                self.save_cache(ranked)
                return [s.url for s in ranked[:n]]

        # Fresh discovery
        logger.info("Discovering fresh sources")
        sources = self.scrape_sources()
        test_results = self.test_all_sources(sources)
        ranked = self.rank_sources(test_results)
        self.save_cache(ranked)

        return [s.url for s in ranked[:n]]


# -------------------- Convenience Function --------------------

def get_best_sources(n: int = 3, force_refresh: bool = False) -> List[str]:
    """Get the n best Sci-Hub sources.

    Args:
        n: Number of sources to return
        force_refresh: Force cache refresh

    Returns:
        List of URLs for the best sources
    """
    manager = SourceManager()
    return manager.get_best_sources(n=n, force_refresh=force_refresh)
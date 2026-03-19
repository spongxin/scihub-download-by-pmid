"""Tests for source_manager module."""

import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

import pytest
from bs4 import BeautifulSoup

from scihub_download.source_manager import SourceManager, SourceStatus, get_best_sources


class TestSourceStatus:
    """Tests for SourceStatus dataclass."""

    def test_source_status_fields(self):
        """Verify SourceStatus fields exist and work correctly."""
        status = SourceStatus(
            url="https://sci-hub.se",
            success_count=5,
            total_attempts=10,
            avg_response_time_ms=150.0,
            last_checked="2024-01-01T00:00:00"
        )
        assert status.url == "https://sci-hub.se"
        assert status.success_count == 5
        assert status.total_attempts == 10
        assert status.avg_response_time_ms == 150.0

    def test_available_property(self):
        """Test available property computation."""
        status_available = SourceStatus(url="https://test.com", success_count=1, total_attempts=1)
        status_unavailable = SourceStatus(url="https://test.com", success_count=0, total_attempts=0)
        assert status_available.available is True
        assert status_unavailable.available is False

    def test_success_rate(self):
        """Test success_rate calculation."""
        status = SourceStatus(url="https://test.com", success_count=7, total_attempts=10)
        assert status.success_rate == 70.0

    def test_success_rate_zero_attempts(self):
        """Test success_rate when no attempts."""
        status = SourceStatus(url="https://test.com", success_count=0, total_attempts=0)
        assert status.success_rate == 0.0


class TestSourceManagerDefaults:
    """Tests for default values."""

    def test_default_sources(self):
        """Verify DEFAULT_SCI_HUB_SOURCES contains expected domains."""
        assert "https://sci-hub.se" in SourceManager.DEFAULT_SCI_HUB_SOURCES
        assert "https://sci-hub.ru" in SourceManager.DEFAULT_SCI_HUB_SOURCES

    def test_cache_file_path(self):
        """Verify CACHE_FILE is in ~/.scihub_download/."""
        # After expanduser, should contain .scihub_download
        assert ".scihub_download" in SourceManager.CACHE_FILE
        assert "sources_cache.json" in SourceManager.CACHE_FILE

    def test_cache_ttl(self):
        """Verify CACHE_TTL_HOURS = 24."""
        assert SourceManager.CACHE_TTL_HOURS == 24


class TestScrapeSources:
    """Tests for scrape_sources method."""

    @patch('scihub_download.source_manager.requests.Session')
    def test_scrape_sources_fallback(self, mock_session_class):
        """Mock requests to fail, verify returns DEFAULT_SCI_HUB_SOURCES."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.get.side_effect = Exception("Network error")

        manager = SourceManager(session=mock_session)
        result = manager.scrape_sources()

        assert result == SourceManager.DEFAULT_SCI_HUB_SOURCES

    @patch('scihub_download.source_manager.requests.Session')
    def test_scrape_sources_parses_html(self, mock_session_class):
        """Mock successful response with sci-hub links, verify extraction."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        html = """
        <html>
            <a href="https://sci-hub.se">Sci-Hub SE</a>
            <a href="https://sci-hub.ru">Sci-Hub RU</a>
            <a href="https://sci-hub.red">Sci-Hub RED</a>
        </html>
        """
        mock_response = Mock()
        mock_response.text = html
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        manager = SourceManager(session=mock_session)
        result = manager.scrape_sources()

        assert "https://sci-hub.se" in result
        assert "https://sci-hub.ru" in result
        assert "https://sci-hub.red" in result


class TestTestSource:
    """Tests for test_source method."""

    @patch('scihub_download.source_manager.requests.Session')
    def test_test_source_success(self, mock_session_class):
        """Mock HEAD request returning 200, verify available=True."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_session.head.return_value = mock_response

        with patch('scihub_download.source_manager.time.time', return_value=0):
            with patch('scihub_download.source_manager.time.time', return_value=0.1):
                manager = SourceManager(session=mock_session)
                status = manager.test_source("https://sci-hub.se")

        assert status.available is True
        assert status.total_attempts == 1
        assert status.success_count == 1

    @patch('scihub_download.source_manager.requests.Session')
    def test_test_source_timeout(self, mock_session_class):
        """Mock timeout, verify available=False."""
        import requests
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.head.side_effect = requests.exceptions.Timeout()

        manager = SourceManager(session=mock_session)
        status = manager.test_source("https://sci-hub.se")

        assert status.available is False
        assert status.total_attempts == 1
        assert status.success_count == 0


class TestRankSources:
    """Tests for rank_sources method."""

    def test_rank_sources_by_success_rate(self):
        """Create sources with different success rates, verify sorted correctly."""
        sources = [
            SourceStatus(url="low", success_count=1, total_attempts=10),
            SourceStatus(url="high", success_count=9, total_attempts=10),
            SourceStatus(url="mid", success_count=5, total_attempts=10),
        ]
        manager = SourceManager()
        ranked = manager.rank_sources(sources)

        assert ranked[0].url == "high"
        assert ranked[1].url == "mid"
        assert ranked[2].url == "low"

    def test_rank_sources_tiebreaker(self):
        """Create sources with same success rate, verify response_time is tiebreaker."""
        sources = [
            SourceStatus(url="slow", success_count=5, total_attempts=10, avg_response_time_ms=500.0),
            SourceStatus(url="fast", success_count=5, total_attempts=10, avg_response_time_ms=100.0),
        ]
        manager = SourceManager()
        ranked = manager.rank_sources(sources)

        assert ranked[0].url == "fast"
        assert ranked[1].url == "slow"


class TestCache:
    """Tests for cache methods."""

    def test_is_cache_valid_missing_file(self):
        """Missing cache file returns False."""
        manager = SourceManager()
        manager.CACHE_FILE = "/nonexistent/path/cache.json"
        assert manager.is_cache_valid() is False

    def test_save_and_load_cache(self):
        """Test saving and loading cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SourceManager()
            manager.CACHE_FILE = os.path.join(tmpdir, "cache.json")

            sources = [
                SourceStatus(url="https://test1.com", success_count=5, total_attempts=10),
                SourceStatus(url="https://test2.com", success_count=3, total_attempts=10),
            ]
            manager.save_cache(sources)

            loaded = manager.load_cache()
            assert len(loaded) == 2
            assert "https://test1.com" in loaded
            assert loaded["https://test1.com"].success_count == 5


class TestGetBestSources:
    """Tests for convenience function."""

    @patch('scihub_download.source_manager.SourceManager')
    def test_get_best_sources_default(self, mock_manager_class):
        """Test get_best_sources convenience function."""
        mock_manager = MagicMock()
        mock_manager.get_best_sources.return_value = ["https://sci-hub.se", "https://sci-hub.ru"]
        mock_manager_class.return_value = mock_manager

        result = get_best_sources(n=3)

        mock_manager.get_best_sources.assert_called_once_with(n=3, force_refresh=False)
        assert result == ["https://sci-hub.se", "https://sci-hub.ru"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
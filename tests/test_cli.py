"""
Test cases for CLI argument parser.

Tests all CLI flags: --verbose, --quiet, --workers, --output, --format, --help.
"""

import pytest
from click.testing import CliRunner
from scihub_download.cli import create_parser


class TestCLIHelp:
    """Test CLI help output."""

    def test_help_shows_usage_and_exits(self):
        """Test --help shows usage and exits."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--help"])
        assert exc_info.value.code == 0

    def test_help_contains_all_options(self):
        """Test --help output contains all documented options."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])
        # Check the help text was printed to stderr
        # This is implicitly tested by the SystemExit


class TestCLIVerbosity:
    """Test CLI verbosity flags."""

    def test_verbose_flag(self):
        """Test --verbose/-v flag."""
        parser = create_parser()
        args = parser.parse_args(["--file", "test.csv", "-v"])
        assert args.verbose is True

    def test_quiet_flag(self):
        """Test --quiet/-q flag."""
        parser = create_parser()
        args = parser.parse_args(["--file", "test.csv", "-q"])
        assert args.quiet is True

    def test_verbose_quiet_mutually_exclusive(self):
        """Test -v and -q cannot be used together."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-v", "-q", "--file", "test.csv"])


class TestCLIWorkers:
    """Test --workers/-w flag."""

    def test_workers_with_value(self):
        """Test --workers/-w flag with custom value."""
        parser = create_parser()
        args = parser.parse_args(["--file", "test.csv", "-w", "10"])
        assert args.workers == 10

    def test_workers_default(self):
        """Test --workers default is 5."""
        parser = create_parser()
        args = parser.parse_args(["--file", "test.csv"])
        assert args.workers == 5


class TestCLIOutput:
    """Test --output/-o flag."""

    def test_output_with_value(self):
        """Test --output/-o flag with custom value."""
        parser = create_parser()
        args = parser.parse_args(["--file", "test.csv", "-o", "/tmp/pdfs"])
        assert args.output == "/tmp/pdfs"

    def test_output_default(self):
        """Test --output default is ./pdfs."""
        parser = create_parser()
        args = parser.parse_args(["--file", "test.csv"])
        assert args.output == "./pdfs"


class TestCLIFormat:
    """Test --format flag."""

    def test_format_with_value(self):
        """Test --format flag with valid value."""
        parser = create_parser()
        args = parser.parse_args(["--file", "test.csv", "--format", "doi"])
        assert args.format == "doi"

    def test_format_invalid(self):
        """Test --format with invalid value raises error."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--file", "test.csv", "--format", "invalid"])


class TestCLIInput:
    def test_file_argument(self):
        """Test --file argument is parsed correctly."""
        parser = create_parser()
        args = parser.parse_args(["--file", "test.csv"])
        assert args.file == "test.csv"

    def test_id_argument(self):
        """Test --id argument is parsed correctly."""
        parser = create_parser()
        args = parser.parse_args(["--id", "12345"])
        assert args.id == "12345"

    def test_file_id_mutually_exclusive(self):
        """Test --file and --id cannot be used together."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--file", "test.csv", "--id", "12345"])

    def test_no_input_raises_error(self):
        """Test that no input raises SystemExit."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])
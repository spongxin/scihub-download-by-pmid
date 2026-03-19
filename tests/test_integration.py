"""Integration tests for CLI and input parser."""
import subprocess
import sys


def test_help_via_module():
    """Test python -m scihub_download --help works."""
    result = subprocess.run(
        [sys.executable, "-m", "scihub_download", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "scihub-download" in result.stdout
    assert "--file" in result.stdout
    assert "--verbose" in result.stdout


def test_single_id_integration():
    """Test end-to-end single ID processing."""
    result = subprocess.run(
        ["scihub-download", "--id", "12345"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Processing single ID" in result.stdout
    assert "12345" in result.stdout


def test_csv_input_integration():
    """Test end-to-end CSV input processing."""
    import tempfile
    from pathlib import Path
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write("PMID,DOI\n12345,10.1234/test\n")
        csv_path = f.name
    try:
        result = subprocess.run(
            ["scihub-download", "--file", csv_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Check for Chinese log output "Using X sources"
        assert "Using" in result.stdout or "using" in result.stderr.lower()
    finally:
        Path(csv_path).unlink()


def test_txt_input_integration():
    """Test end-to-end TXT input processing."""
    import tempfile
    from pathlib import Path
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("12345\n10.1234/test\n")
        txt_path = f.name
    try:
        result = subprocess.run(
            ["scihub-download", "--file", txt_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # TXT files are converted to CSV by input_parser, check for download attempt
        assert "Using" in result.stdout or "using" in result.stderr.lower()
    finally:
        Path(txt_path).unlink()
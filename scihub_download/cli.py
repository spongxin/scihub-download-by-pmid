"""CLI argument parser for scihub-download."""
import argparse
import sys
from typing import Optional, List

from .input_parser import parse_input_file, parse_single_id
from .downloader import main as downloader_main


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser for scihub-download CLI
    """
    parser = argparse.ArgumentParser(
        prog="scihub-download",
        description="Download PDFs from Sci-Hub using PMID/DOI identifiers.",
        epilog="Example: scihub-download --file papers.csv --output ./pdfs -w 10"
    )

    # Mutually exclusive input group (required)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-f", "--file", type=str, metavar="PATH",
                             help="Input file (CSV, TXT, or XLSX format)")
    input_group.add_argument("--id", type=str, metavar="IDENTIFIER",
                             help="Single PMID or DOI to download")

    # Output options
    parser.add_argument("-o", "--output", type=str, default="./pdfs", metavar="DIR",
                        help="Output directory for PDFs (default: ./pdfs)")
    parser.add_argument("-w", "--workers", type=int, default=5, metavar="N",
                        help="Number of parallel download threads (default: 5)")
    parser.add_argument("--format", type=str, choices=["pmid", "doi", "original"],
                        default="pmid", help="Filename pattern (default: pmid)")

    # Verbosity (mutually exclusive, not required)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose", action="store_true",
                          help="Enable detailed output")
    verbosity.add_argument("-q", "--quiet", action="store_true",
                          help="Suppress non-essential output")

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Print Sci-Hub coverage message (not in quiet mode) - at the very beginning
    if not args.quiet:
        print("Sci-Hub 对 2022 年之前在主要学术出版物上发表的所有论文的覆盖率超过 90%。较新的文章可以在新平台 Sci-Net")
        print("(https://sci-net.xyz/) 上请求获取，这是一个研究人员互助社交网络：您可以发布请求，其他成员会帮助解决。全文通常在几分钟内就会被上传，除了一些特殊情况。一旦上传，论")
        print("文将对所有人免费开放，无需注册。您也可以上传自己的论文，以确保它们永久开放获取。")
        print()
        sys.stdout.flush()  # Ensure message is printed before any logging

    # Parse input - convert to CSV for downloader
    if args.file:
        csv_file = args.file
    else:  # args.id - create temp CSV
        import pandas as pd
        import tempfile
        df = parse_single_id(args.id)
        # Create temporary CSV for downloader
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        csv_file = temp_file.name
        if not args.quiet:
            print(f"Processing single ID: {args.id}")

    # Build argument list for downloader
    downloader_args = ['', csv_file, args.output,
                       '--workers', str(args.workers),
                       '--format', args.format,
                       '--delete-corrupted']
    if args.verbose:
        downloader_args.append('--verbose')
    elif args.quiet:
        downloader_args.append('--quiet')

    # Call downloader main with modified argv
    sys.argv = downloader_args
    downloader_main()
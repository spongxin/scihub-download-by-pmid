"""CLI argument parser for scihub-download."""
import argparse
from typing import Optional, List

from .input_parser import parse_input_file, parse_single_id


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

    # Parse input
    if args.file:
        df = parse_input_file(args.file)
        print(f"Loaded {len(df)} records from {args.file}")
    else:  # args.id
        df = parse_single_id(args.id)
        print(f"Processing single ID: {args.id}")

    # Print configuration summary
    print(f"Output directory: {args.output}")
    print(f"Workers: {args.workers}")
    print(f"Format: {args.format}")
    print(f"Verbose: {args.verbose}")
    print(f"Quiet: {args.quiet}")

    # Placeholder for Phase 3 download logic
    print(f"\nFound {len(df)} records to process.")
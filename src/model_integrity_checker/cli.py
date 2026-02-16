"""CLI interface for model integrity checker."""

import argparse
import json
import sys

from model_integrity_checker import (
    calculate_checksum,
    get_supported_formats,
    load_checksums,
    save_checksums,
    scan_directory,
    verify_checksum,
)


def cmd_calculate(args):
    """Calculate checksum for a model file."""
    try:
        checksum = calculate_checksum(args.model)
        if args.output:
            save_checksums({args.model: checksum}, args.output)
            print(f"Checksum saved to {args.output}")
        else:
            print(checksum)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_verify(args):
    """Verify model file checksum."""
    if args.checksum_file:
        try:
            checksums = load_checksums(args.checksum_file)
            if args.model in checksums:
                expected = checksums[args.model]
            else:
                print(f"Error: Model '{args.model}' not found in checksum file", file=sys.stderr)
                return 1
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        expected = args.checksum

    if verify_checksum(args.model, expected):
        print("✓ Checksum verified successfully")
        return 0
    else:
        print("✗ Checksum mismatch!", file=sys.stderr)
        return 1


def cmd_scan(args):
    """Scan directory for model files."""
    formats = args.formats.split(",") if args.formats else None
    checksums = scan_directory(
        args.directory,
        formats=formats,
        recursive=not args.no_recursive,
    )

    if args.output:
        save_checksums(checksums, args.output)
        print(f"Found {len(checksums)} model file(s). Checksums saved to {args.output}")
    else:
        print(json.dumps(checksums, indent=2))
    return 0


def cmd_formats(args):
    """List supported model formats."""
    for fmt in get_supported_formats():
        print(fmt)
    return 0


def main(args=None):
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Model Integrity Checker - Verify ML model checksums"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    calc_parser = subparsers.add_parser("calculate", help="Calculate checksum for a model")
    calc_parser.add_argument("model", help="Path to model file")
    calc_parser.add_argument("-o", "--output", help="Output file for checksum")

    verify_parser = subparsers.add_parser("verify", help="Verify model checksum")
    verify_parser.add_argument("model", help="Path to model file")
    verify_parser.add_argument("-c", "--checksum", help="Expected checksum value")
    verify_parser.add_argument("-f", "--checksum-file", help="JSON file with checksums")

    scan_parser = subparsers.add_parser("scan", help="Scan directory for model files")
    scan_parser.add_argument("directory", help="Directory to scan")
    scan_parser.add_argument(
        "-f", "--formats", help="Comma-separated list of formats (e.g., .h5,.pt)"
    )
    scan_parser.add_argument(
        "--no-recursive", action="store_true", help="Don't scan subdirectories"
    )
    scan_parser.add_argument("-o", "--output", help="Output file for checksums")

    subparsers.add_parser("formats", help="List supported formats")

    args = parser.parse_args(args)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "calculate":
        return cmd_calculate(args)
    elif args.command == "verify":
        if not args.checksum and not args.checksum_file:
            print("Error: Either --checksum or --checksum-file required", file=sys.stderr)
            return 1
        return cmd_verify(args)
    elif args.command == "scan":
        return cmd_scan(args)
    elif args.command == "formats":
        return cmd_formats(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())

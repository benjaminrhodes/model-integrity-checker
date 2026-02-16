"""Model integrity checker package."""

import hashlib
import json
from pathlib import Path
from typing import Union


SUPPORTED_FORMATS = [".h5", ".pt", ".onnx"]


def get_supported_formats() -> list:
    """Return list of supported model formats."""
    return SUPPORTED_FORMATS.copy()


def calculate_checksum(path: Union[str, Path], algorithm: str = "sha256") -> str:
    """Calculate checksum for a file.

    Args:
        path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)

    Returns:
        Hexadecimal checksum string

    Raises:
        FileNotFoundError: If file does not exist
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if algorithm.lower() == "sha256":
        hasher = hashlib.sha256()
    elif algorithm.lower() == "md5":
        hasher = hashlib.md5()
    elif algorithm.lower() == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()


def verify_checksum(path: Union[str, Path], expected_checksum: str) -> bool:
    """Verify file checksum matches expected value.

    Args:
        path: Path to the file
        expected_checksum: Expected checksum value

    Returns:
        True if checksum matches, False otherwise
    """
    try:
        actual = calculate_checksum(path)
        return actual == expected_checksum
    except (FileNotFoundError, ValueError):
        return False


def save_checksums(checksums: dict, filepath: str) -> None:
    """Save checksums to JSON file.

    Args:
        checksums: Dictionary mapping filenames to checksums
        filepath: Path to save the checksums file
    """
    with open(filepath, "w") as f:
        json.dump(checksums, f, indent=2)


def load_checksums(filepath: str) -> dict:
    """Load checksums from JSON file.

    Args:
        filepath: Path to the checksums file

    Returns:
        Dictionary mapping filenames to checksums

    Raises:
        FileNotFoundError: If file does not exist
    """
    with open(filepath, "r") as f:
        return json.load(f)


def scan_directory(
    directory: Union[str, Path], formats: list = None, recursive: bool = True
) -> dict:
    """Scan directory for model files and calculate checksums.

    Args:
        directory: Directory to scan
        formats: List of file extensions to include (default: all supported)
        recursive: Whether to scan subdirectories

    Returns:
        Dictionary mapping filenames to checksums
    """
    directory = Path(directory)
    if formats is None:
        formats = SUPPORTED_FORMATS

    checksums = {}
    pattern = "**/*" if recursive else "*"

    for ext in formats:
        for path in directory.glob(f"{pattern}{ext}"):
            if path.is_file():
                rel_path = path.relative_to(directory)
                checksums[str(rel_path)] = calculate_checksum(path)

    return checksums

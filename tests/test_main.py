"""Tests for model integrity checker."""

import hashlib
import os
import tempfile
from pathlib import Path

import pytest

from model_integrity_checker import calculate_checksum, verify_checksum, get_supported_formats


class TestCalculateChecksum:
    """Tests for checksum calculation."""

    def test_calculate_sha256_for_file(self):
        """Test SHA256 checksum calculation for a file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            path = f.name

        try:
            expected = hashlib.sha256(b"test content").hexdigest()
            result = calculate_checksum(path)
            assert result == expected
        finally:
            os.unlink(path)

    def test_calculate_checksum_for_nonexistent_file(self):
        """Test checksum calculation for nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            calculate_checksum("/nonexistent/path/model.pt")

    def test_calculate_checksum_empty_file(self):
        """Test checksum for empty file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name

        try:
            expected = hashlib.sha256(b"").hexdigest()
            result = calculate_checksum(path)
            assert result == expected
        finally:
            os.unlink(path)

    def test_calculate_checksum_large_file(self):
        """Test checksum for larger file."""
        content = b"x" * 1024 * 100
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        try:
            expected = hashlib.sha256(content).hexdigest()
            result = calculate_checksum(path)
            assert result == expected
        finally:
            os.unlink(path)


class TestVerifyChecksum:
    """Tests for checksum verification."""

    def test_verify_valid_checksum(self):
        """Test verification with correct checksum."""
        content = b"model data"
        expected_hash = hashlib.sha256(content).hexdigest()

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        try:
            result = verify_checksum(path, expected_hash)
            assert result is True
        finally:
            os.unlink(path)

    def test_verify_invalid_checksum(self):
        """Test verification with incorrect checksum."""
        content = b"model data"

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        try:
            result = verify_checksum(path, "invalid_checksum")
            assert result is False
        finally:
            os.unlink(path)

    def test_verify_nonexistent_file(self):
        """Test verification for nonexistent file."""
        result = verify_checksum("/nonexistent/model.pt", "abc123")
        assert result is False


class TestSupportedFormats:
    """Tests for supported model formats."""

    def test_get_supported_formats(self):
        """Test getting list of supported formats."""
        formats = get_supported_formats()
        assert isinstance(formats, list)
        assert ".h5" in formats
        assert ".pt" in formats
        assert ".onnx" in formats

    def test_supported_formats_are_strings(self):
        """Test that all formats are strings with dot prefix."""
        formats = get_supported_formats()
        for fmt in formats:
            assert isinstance(fmt, str)
            assert fmt.startswith(".")


class TestChecksumFile:
    """Tests for checksum file operations."""

    def test_save_and_load_checksums(self):
        """Test saving and loading checksums from JSON file."""
        from model_integrity_checker import save_checksums, load_checksums

        checksums = {
            "model1.h5": "abc123",
            "model2.pt": "def456",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            checksum_file = Path(tmpdir) / "checksums.json"
            save_checksums(checksums, str(checksum_file))
            loaded = load_checksums(str(checksum_file))
            assert loaded == checksums

    def test_load_nonexistent_checksum_file(self):
        """Test loading nonexistent checksum file raises error."""
        from model_integrity_checker import load_checksums

        with pytest.raises(FileNotFoundError):
            load_checksums("/nonexistent/checksums.json")


class TestPathHandling:
    """Tests for path handling."""

    def test_calculate_checksum_with_pathlib(self):
        """Test checksum calculation with Path object."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            f.flush()
            path = Path(f.name)

        try:
            expected = hashlib.sha256(b"test").hexdigest()
            result = calculate_checksum(path)
            assert result == expected
        finally:
            os.unlink(path)

    def test_calculate_checksum_with_string_path(self):
        """Test checksum calculation with string path."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            f.flush()
            path = f.name

        try:
            expected = hashlib.sha256(b"test").hexdigest()
            result = calculate_checksum(path)
            assert result == expected
        finally:
            os.unlink(path)

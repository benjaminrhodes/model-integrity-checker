"""Tests for CLI."""

import json
import os
import tempfile

from model_integrity_checker.cli import main


class TestCLI:
    """Tests for CLI commands."""

    def test_formats_command(self, capsys):
        """Test formats command."""
        result = main(["formats"])
        assert result == 0
        captured = capsys.readouterr()
        assert ".h5" in captured.out
        assert ".pt" in captured.out
        assert ".onnx" in captured.out

    def test_calculate_command(self, capsys):
        """Test calculate command."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            path = f.name

        try:
            result = main(["calculate", path])
            assert result == 0
            captured = capsys.readouterr()
            assert len(captured.out.strip()) == 64
        finally:
            os.unlink(path)

    def test_calculate_nonexistent_file(self, capsys):
        """Test calculate with nonexistent file."""
        result = main(["calculate", "/nonexistent/model.pt"])
        assert result == 1

    def test_calculate_with_output(self):
        """Test calculate with output file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            f.flush()
            path = f.name

        with tempfile.NamedTemporaryFile(delete=False) as out:
            outpath = out.name

        try:
            result = main(["calculate", path, "-o", outpath])
            assert result == 0
            with open(outpath) as f:
                data = json.load(f)
            assert path in data
        finally:
            os.unlink(path)
            os.unlink(outpath)

    def test_verify_valid_checksum(self, capsys):
        """Test verify with valid checksum."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            path = f.name

        from model_integrity_checker import calculate_checksum

        checksum = calculate_checksum(path)

        try:
            result = main(["verify", path, "-c", checksum])
            assert result == 0
            captured = capsys.readouterr()
            assert "verified" in captured.out.lower()
        finally:
            os.unlink(path)

    def test_verify_invalid_checksum(self, capsys):
        """Test verify with invalid checksum."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            path = f.name

        try:
            result = main(["verify", path, "-c", "invalid_checksum"])
            assert result == 1
        finally:
            os.unlink(path)

    def test_verify_with_checksum_file(self):
        """Test verify with checksum file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            path = f.name

        from model_integrity_checker import calculate_checksum

        checksum = calculate_checksum(path)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump({path: checksum}, f)
            f.flush()
            checksum_file = f.name

        try:
            result = main(["verify", path, "-f", checksum_file])
            assert result == 0
        finally:
            os.unlink(path)
            os.unlink(checksum_file)

    def test_scan_command(self, capsys):
        """Test scan command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "model.h5"), "w") as f:
                f.write("fake model")
            with open(os.path.join(tmpdir, "model2.pt"), "w") as f:
                f.write("fake model 2")

            result = main(["scan", tmpdir])
            assert result == 0
            captured = capsys.readouterr()
            data = json.loads(captured.out)
            assert len(data) == 2

    def test_scan_with_output(self):
        """Test scan with output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "model.h5"), "w") as f:
                f.write("fake model")

            with tempfile.NamedTemporaryFile(delete=False) as out:
                outpath = out.name

            result = main(["scan", tmpdir, "-o", outpath])
            assert result == 0

            with open(outpath) as f:
                data = json.load(f)
            assert len(data) == 1

            os.unlink(outpath)

    def test_no_command(self, capsys):
        """Test with no command shows help."""
        result = main([])
        assert result == 1

    def test_verify_requires_checksum(self, capsys):
        """Test verify requires checksum argument."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            f.flush()
            path = f.name

        try:
            result = main(["verify", path])
            assert result == 1
        finally:
            os.unlink(path)

# Model Integrity Checker

Verify ML model checksums to ensure model integrity.

## Features

- Calculate model checksums (SHA256)
- Verify model integrity
- Support common model formats (.h5, .pt, .onnx)
- CLI interface
- Scan directories for model files
- Save/load checksums from JSON files

## Installation

```bash
pip install model-integrity-checker
```

## Usage

### Calculate checksum for a model file

```bash
model-checker calculate model.pt
# Output: <sha256-checksum>

# Save checksum to file
model-checker calculate model.pt -o checksums.json
```

### Verify model integrity

```bash
# Verify with checksum on command line
model-checker verify model.pt -c <sha256-checksum>

# Verify with checksum file
model-checker verify model.pt -f checksums.json
```

### Scan directory for model files

```bash
# Scan current directory (recursive)
model-checker scan ./models

# Scan with specific formats
model-checker scan ./models -f .h5,.pt

# Scan non-recursively
model-checker scan ./models --no-recursive

# Save checksums to file
model-checker scan ./models -o checksums.json
```

### List supported formats

```bash
model-checker formats
# Output:
# .h5
# .pt
# .onnx
```

## Python API

```python
from model_integrity_checker import (
    calculate_checksum,
    verify_checksum,
    get_supported_formats,
    save_checksums,
    load_checksums,
    scan_directory,
)

# Calculate checksum
checksum = calculate_checksum("model.pt")

# Verify checksum
is_valid = verify_checksum("model.pt", expected_checksum)

# Get supported formats
formats = get_supported_formats()

# Scan directory
checksums = scan_directory("./models")
```

## Testing

```bash
pytest tests/ -v --cov=model_integrity_checker
```

## License

MIT

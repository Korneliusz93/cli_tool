"""Test configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import os


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    # Create test files
    (temp_dir / "test1.txt").write_text("Hello World")
    (temp_dir / "test2.log").write_text("Log entry")
    (temp_dir / "subdir").mkdir()
    (temp_dir / "subdir" / "nested.txt").write_text("Nested file")

    return temp_dir

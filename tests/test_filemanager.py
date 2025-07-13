"""Tests for file management utilities."""

import pytest
from pathlib import Path
from linux_cli_utils.filemanager import get_file_info, format_size, find_files


def test_format_size():
    """Test file size formatting."""
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024 * 1024) == "1.0 MB"
    assert format_size(1024 * 1024 * 1024) == "1.0 GB"
    assert format_size(512) == "512.0 B"


def test_get_file_info(sample_files):
    """Test getting file information."""
    test_file = sample_files / "test1.txt"
    info = get_file_info(test_file)

    assert info["is_file"] is True
    assert info["is_dir"] is False
    assert info["size"] == 11  # "Hello World" length
    assert "permissions" in info
    assert "modified" in info


def test_find_files(sample_files):
    """Test finding files."""
    files = find_files(sample_files, "*.txt")

    # Should find test1.txt and nested.txt
    assert len(files) >= 2
    assert any(f.name == "test1.txt" for f in files)
    assert any(f.name == "nested.txt" for f in files)


def test_find_files_with_pattern(sample_files):
    """Test finding files with specific pattern."""
    files = find_files(sample_files, "*.log")

    # Should find test2.log
    assert len(files) == 1
    assert files[0].name == "test2.log"


def test_find_directories(sample_files):
    """Test finding directories."""
    dirs = find_files(sample_files, "*", file_type="dirs")

    # Should find subdir
    assert len(dirs) >= 1
    assert any(d.name == "subdir" for d in dirs)

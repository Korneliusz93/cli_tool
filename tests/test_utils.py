"""Tests for common utility functions."""

import pytest
from unittest.mock import patch, MagicMock
from linux_cli_utils.utils import (
    run_command, 
    run_command_with_output, 
    format_size, 
    format_time,
    check_command_exists
)


def test_format_size():
    """Test file size formatting."""
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024 * 1024) == "1.0 MB"
    assert format_size(1024 * 1024 * 1024) == "1.0 GB"
    assert format_size(512) == "512.0 B"


def test_format_time():
    """Test time formatting."""
    # Test with a known timestamp (2025-01-01 00:00:00 UTC)
    timestamp = 1735689600
    result = format_time(timestamp)
    assert "2025" in result
    # Just check the format, not the exact time due to timezone differences
    assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format


@patch('subprocess.run')
def test_run_command_success(mock_run):
    """Test successful command execution."""
    mock_result = MagicMock()
    mock_result.stdout = "test output"
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    result = run_command("echo test")
    assert result == "test output"


@patch('subprocess.run')
def test_run_command_failure(mock_run):
    """Test command failure handling."""
    from subprocess import CalledProcessError
    mock_run.side_effect = CalledProcessError(1, "invalid_command")
    
    result = run_command("invalid_command")
    assert result is None


@patch('subprocess.run')
def test_run_command_with_output(mock_run):
    """Test detailed command output."""
    mock_result = MagicMock()
    mock_result.stdout = "success output"
    mock_result.stderr = ""
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    result = run_command_with_output("echo test")
    
    assert result['success'] is True
    assert result['stdout'] == "success output"
    assert result['returncode'] == 0


@patch('linux_cli_utils.utils.run_command')
def test_check_command_exists(mock_run_command):
    """Test command existence checking."""
    # Test existing command
    mock_run_command.return_value = "/usr/bin/ls"
    assert check_command_exists("ls") is True
    
    # Test non-existing command
    mock_run_command.return_value = None
    assert check_command_exists("nonexistent_command") is False


def test_format_size_edge_cases():
    """Test edge cases for format_size."""
    assert format_size(0) == "0.0 B"
    assert format_size(1) == "1.0 B"
    assert format_size(1023) == "1023.0 B"

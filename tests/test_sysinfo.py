"""Tests for system information utilities."""

import pytest
from unittest.mock import patch, MagicMock
from linux_cli_utils.sysinfo import get_cpu_info, get_memory_info, run_command


def test_run_command():
    """Test running system commands."""
    # Test with a simple command that should work on most systems
    result = run_command("echo test")
    assert result == "test"


@patch("subprocess.run")
def test_run_command_failure(mock_run):
    """Test command failure handling."""
    from subprocess import CalledProcessError

    mock_run.side_effect = CalledProcessError(1, "invalid_command")
    result = run_command("invalid_command")
    assert result is None


@patch("psutil.cpu_percent")
@patch("subprocess.run")
def test_get_cpu_info(mock_run, mock_cpu):
    """Test getting CPU information."""
    # Mock lscpu output
    mock_result = MagicMock()
    mock_result.stdout = "Model name: Intel Core i7\nCPU(s): 8\nCPU max MHz: 3000"
    mock_result.returncode = 0
    mock_run.return_value = mock_result

    mock_cpu.return_value = 25.5

    cpu_info = get_cpu_info()

    assert "usage" in cpu_info
    assert cpu_info["usage"] == "25.5%"


@patch("psutil.virtual_memory")
@patch("psutil.swap_memory")
def test_get_memory_info(mock_swap, mock_memory):
    """Test getting memory information."""
    # Mock memory info
    mock_memory.return_value = MagicMock(
        total=8589934592,  # 8 GB
        available=4294967296,  # 4 GB
        used=4294967296,  # 4 GB
        percent=50.0,
    )

    mock_swap.return_value = MagicMock(
        total=2147483648, used=1073741824, percent=50.0  # 2 GB  # 1 GB
    )

    memory_info = get_memory_info()

    assert "total" in memory_info
    assert "available" in memory_info
    assert "used" in memory_info
    assert "usage" in memory_info
    assert memory_info["usage"] == "50.0%"

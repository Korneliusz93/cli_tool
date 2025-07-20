"""Common utility functions used across Linux CLI utilities."""

import subprocess
from typing import Optional, List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_command(cmd: str, shell: bool = True, check: bool = True) -> Optional[str]:
    """Run a shell command and return its output.
    
    Args:
        cmd: Command to execute
        shell: Whether to run through shell
        check: Whether to raise exception on non-zero exit
        
    Returns:
        Command output as string, or None if command failed
    """
    try:
        if shell:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
        else:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                check=check
            )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.warning(f"Command failed: {cmd} - {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error running command: {cmd} - {e}")
        return None


def run_command_with_output(cmd: str, shell: bool = True) -> Dict[str, Any]:
    """Run a command and return detailed output information.
    
    Args:
        cmd: Command to execute
        shell: Whether to run through shell
        
    Returns:
        Dict containing stdout, stderr, returncode, and success status
    """
    try:
        if shell:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True
            )
        
        return {
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode,
            'success': result.returncode == 0
        }
    except Exception as e:
        logger.error(f"Error running command: {cmd} - {e}")
        return {
            'stdout': '',
            'stderr': str(e),
            'returncode': -1,
            'success': False
        }


def format_size(size: int) -> str:
    """Format file size in human readable format.
    
    Args:
        size: Size in bytes
        
    Returns:
        Human readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def format_time(timestamp: float) -> str:
    """Format timestamp to readable time.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted time string
    """
    import time
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def check_command_exists(command: str) -> bool:
    """Check if a command exists in the system PATH.
    
    Args:
        command: Command name to check
        
    Returns:
        True if command exists, False otherwise
    """
    result = run_command(f"which {command}", check=False)
    return result is not None


def ensure_directory(path: str) -> bool:
    """Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Directory path to create
        
    Returns:
        True if directory exists or was created, False on error
    """
    from pathlib import Path
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def is_root() -> bool:
    """Check if running as root user.
    
    Returns:
        True if running as root, False otherwise
    """
    import os
    return os.geteuid() == 0


def get_system_info() -> Dict[str, str]:
    """Get basic system information.
    
    Returns:
        Dict containing system information
    """
    info = {}
    
    # Get system info
    uname_output = run_command("uname -a")
    if uname_output:
        info['system'] = uname_output
    
    # Get OS release info
    os_release = run_command("cat /etc/os-release")
    if os_release:
        for line in os_release.split('\n'):
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                info[key.lower()] = value.strip('"')
    
    return info

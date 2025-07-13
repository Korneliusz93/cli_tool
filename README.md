# Linux CLI Utilities

A collection of Python-based command line utilities designed for openSUSE Linux and other Linux distributions.

## Features

- **System Information Tools**: Get detailed system information and hardware specs
- **File Management Utilities**: Advanced file operations and organization tools
- **Network Utilities**: Network monitoring and configuration helpers
- **Process Management**: Enhanced process monitoring and management tools

## Installation

1. Clone or download this project
2. Create a virtual environment (already configured):
   ```bash
   # Virtual environment is already set up at .venv/
   source .venv/bin/activate  # If needed
   ```
3. Install dependencies (already installed):
   ```bash
   pip install -r requirements.txt
   ```
4. Install the package in development mode (already done):
   ```bash
   pip install -e .
   ```

## Quick Usage

The easiest way to use the utilities is through the `cli.sh` script:

```bash
./cli.sh help                    # Show available commands
./cli.sh sysinfo overview        # System overview
./cli.sh sysinfo memory          # Memory information
./cli.sh file ls -l              # Enhanced directory listing
./cli.sh net interfaces          # Network interfaces
./cli.sh proc top -l 10          # Top 10 processes
./cli.sh test                    # Run tests
```

## Detailed Usage

Each utility can be run directly using Python modules:

### System Information (`sysinfo`)

```bash
# System overview with CPU, memory, and system info
.venv/bin/python -m linux_cli_utils.sysinfo overview

# Detailed CPU information
.venv/bin/python -m linux_cli_utils.sysinfo cpu

# Memory and swap information
.venv/bin/python -m linux_cli_utils.sysinfo memory

# Disk usage information
.venv/bin/python -m linux_cli_utils.sysinfo disk

# Network interface information
.venv/bin/python -m linux_cli_utils.sysinfo network
```

### File Manager (`filemanager`)

```bash
# Enhanced directory listing
.venv/bin/python -m linux_cli_utils.filemanager ls -l

# Find files with pattern
.venv/bin/python -m linux_cli_utils.filemanager find -p "*.py"

# Directory tree view
.venv/bin/python -m linux_cli_utils.filemanager tree -d 3

# Disk usage analysis
.venv/bin/python -m linux_cli_utils.filemanager du -h
```

### Network Tools (`nettools`)

```bash
# Show network interfaces
.venv/bin/python -m linux_cli_utils.nettools interfaces

# Ping a host
.venv/bin/python -m linux_cli_utils.nettools ping google.com

# Scan ports on a host
.venv/bin/python -m linux_cli_utils.nettools portscan localhost -p "22,80,443"

# Show routing table
.venv/bin/python -m linux_cli_utils.nettools routes

# Network connection status
.venv/bin/python -m linux_cli_utils.nettools netstat
```

### Process Tools (`proctools`)

```bash
# List running processes
.venv/bin/python -m linux_cli_utils.proctools ps -l 20

# Top processes by CPU usage
.venv/bin/python -m linux_cli_utils.proctools top -l 10

# Detailed process information
.venv/bin/python -m linux_cli_utils.proctools info 1234

# Find processes by name
.venv/bin/python -m linux_cli_utils.proctools find firefox

# Kill a process
.venv/bin/python -m linux_cli_utils.proctools kill 1234

# Real-time process monitor
.venv/bin/python -m linux_cli_utils.proctools monitor
```

## VS Code Integration

This project is configured for VS Code with:

- **Tasks**: Use Ctrl+Shift+P → "Tasks: Run Task" to run predefined tasks
- **Debug Configurations**: Use F5 to debug individual utilities
- **Python Environment**: Automatically configured virtual environment
- **Tests**: Run with the "Run Tests" task or `./cli.sh test`

Available VS Code tasks:
- Run Linux CLI Utils
- System Info Overview
- File Manager List
- Network Interfaces
- Process Top
- Run Tests
- Format Code
- Install Package

## Development

### Running Tests

```bash
./cli.sh test
# or
.venv/bin/python -m pytest tests/ -v
```

### Code Formatting

```bash
./cli.sh format
# or
.venv/bin/python -m black src/ tests/
```

### Adding New Utilities

1. Create a new module in `src/linux_cli_utils/`
2. Follow the existing pattern using `typer` and `rich`
3. Add tests in `tests/`
4. Update the main CLI in `cli.py`
5. Add commands to `cli.sh`

## Requirements

- Python 3.8+
- openSUSE Linux (or other Linux distributions)
- Standard Linux utilities (ps, df, lscpu, ip, etc.)

## Dependencies

- `typer` - Modern CLI framework
- `rich` - Beautiful terminal output
- `psutil` - System and process utilities
- `click` - Command line interface creation
- `colorama` - Cross-platform colored terminal text

## Project Structure

```
console_apps/
├── src/linux_cli_utils/     # Main package
│   ├── __init__.py
│   ├── cli.py              # Main CLI entry point
│   ├── sysinfo.py          # System information utilities
│   ├── filemanager.py      # File management utilities
│   ├── nettools.py         # Network utilities
│   └── proctools.py        # Process management utilities
├── tests/                  # Test suite
├── .vscode/               # VS Code configuration
├── .github/               # GitHub and Copilot instructions
├── cli.sh                 # Quick command script
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## License

MIT License - see LICENSE file for details.

## AI Assistance

Parts of this script were assisted by AI tools, including:
- GitHub Copilot (code scaffolding and syntax help)
- Claude (logic suggestions and refactoring)

All output was reviewed and tested by me on openSUSE Linux.


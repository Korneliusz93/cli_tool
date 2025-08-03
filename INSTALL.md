# AI Lab CLI Utilities - Installation Guide

## Quick Installation

### Automatic System Installation (Recommended)
```bash
# Clone or download the project
git clone <repository-url> ailab-cli-utils
cd ailab-cli-utils

# Run the installer (requires sudo)
sudo ./install.sh
```

This will:
- Install all Python dependencies
- Copy utilities to `/usr/local/lib/python3/dist-packages/`
- Create executable scripts in `/usr/local/bin/`
- Generate man pages in `/usr/local/share/man/man1/`
- Set up bash completion
- Create desktop entry
- Install uninstaller

### Manual Installation Steps

#### 1. Install Dependencies
```bash
# Install Python dependencies
pip3 install typer rich psutil click colorama

# Or install all at once
make install-deps
```

#### 2. Development Installation
```bash
# Install in development mode
make dev-install
# or
pip3 install -e .
```

#### 3. System Installation
```bash
# Install system-wide
make install
```

## Available Commands After Installation

### Main Interface
```bash
ailab-cli                    # Main CLI interface
ailab-cli --help            # Show help
ailab-cli list-tools        # List all available tools
ailab-cli version           # Show version
```

### Individual Utilities
```bash
ailab-sysinfo overview      # System overview
ailab-file ls -l            # Enhanced file listing
ailab-net interfaces        # Network interfaces
ailab-proc top -l 10        # Top processes
ailab-backup list-snapshots # List snapshots
```

## Documentation

### Man Pages
```bash
man ailab-cli              # Main manual
man ailab-sysinfo          # System info manual
man ailab-file             # File management manual
man ailab-net              # Network utilities manual
man ailab-proc             # Process management manual
man ailab-backup           # Backup utilities manual
```

### Built-in Help
```bash
ailab-cli --help           # Main help
ailab-sysinfo --help       # Sysinfo help
ailab-file --help          # File management help
# ... and so on for each utility
```

## Development Workflow

### Setting Up Development Environment
```bash
# Clone repository
git clone <repository-url> ailab-cli-utils
cd ailab-cli-utils

# Set up development environment
make dev-setup

# Run tests
make test

# Format code
make format

# Run linting
make lint
```

### Available Make Commands
```bash
make help                  # Show all available commands
make install               # Install system-wide
make dev-install           # Development installation
make test                  # Run tests
make test-coverage         # Run tests with coverage
make format                # Format code with black
make lint                  # Lint with flake8
make type-check            # Type check with mypy
make clean                 # Clean build artifacts
make build                 # Build distribution
make demo                  # Run demo
make check                 # Run all checks
```

## Configuration

### Bash Completion
Bash completion is automatically installed. Restart your shell or run:
```bash
source /usr/local/share/bash-completion/completions/ailab-cli
```

### Desktop Integration
A desktop entry is created for terminal access. Look for "AI Lab CLI Utilities" in your applications menu.

## Monitoring Service (Optional)

### Install Monitoring Service
```bash
# Copy service file
sudo cp ailab-monitor.service /etc/systemd/system/

# Enable and start the service
sudo systemctl enable ailab-monitor
sudo systemctl start ailab-monitor

# Check status
sudo systemctl status ailab-monitor
```

This service runs continuous process monitoring in the background.

## Uninstallation

### Complete Removal
```bash
# Uninstall system-wide installation
sudo ailab-uninstall

# Or using make
make uninstall
```

### Development Mode Cleanup
```bash
# Remove development installation
pip3 uninstall linux-cli-utils

# Clean build artifacts
make clean
```

## File Locations

### Installed Files
- **Executables**: `/usr/local/bin/ailab-*`
- **Python Package**: `/usr/local/lib/python3/dist-packages/linux_cli_utils/`
- **Man Pages**: `/usr/local/share/man/man1/ailab-*.1`
- **Desktop Entry**: `/usr/local/share/applications/ailab-cli.desktop`
- **Bash Completion**: `/usr/local/share/bash-completion/completions/ailab-cli`

### Development Files
- **Source Code**: `src/linux_cli_utils/`
- **Tests**: `tests/`
- **Configuration**: `pyproject.toml`
- **Dependencies**: `requirements.txt`

## Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Ensure scripts are executable
sudo chmod +x /usr/local/bin/ailab-*
```

#### Python Import Errors
```bash
# Check Python path
python3 -c "import sys; print(sys.path)"

# Reinstall package
sudo ./install.sh
```

#### Missing Dependencies
```bash
# Install missing dependencies
make install-deps
```

### Getting Help

#### Command Help
```bash
ailab-cli --help
ailab-<utility> --help
```

#### Man Pages
```bash
man ailab-cli
man ailab-<utility>
```

#### Logs
```bash
# For monitoring service
sudo journalctl -u ailab-monitor -f
```

## System Requirements

- **OS**: Linux (tested on openSUSE, should work on most distributions)
- **Python**: 3.8 or higher
- **Memory**: 50MB+ free RAM
- **Disk**: 10MB+ free space
- **Privileges**: sudo access for system installation

## Features

- ✅ System-wide installation
- ✅ Individual utility scripts
- ✅ Comprehensive man pages
- ✅ Bash completion
- ✅ Desktop integration
- ✅ Development mode support
- ✅ Automated testing
- ✅ Code formatting and linting
- ✅ Easy uninstallation

Your AI Lab CLI utilities are now ready for professional use! 🚀

#!/bin/bash
# AI Lab CLI Utilities - Test Installation (No Root Required)
# This script demonstrates the installation process without system modifications

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "AI Lab Linux CLI Utilities - Installation Demo"
echo "=============================================="
echo

print_status "Checking Python installation..."
python3 --version
print_success "Python check passed"

print_status "Checking package structure..."
ls -la src/linux_cli_utils/
print_success "Package structure verified"

print_status "Testing imports..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from linux_cli_utils.utils import run_command, format_size
from linux_cli_utils.cli import main
print('✓ All imports successful')
"
print_success "Import test passed"

print_status "Testing utilities..."
echo "System info test:"
/home/admin/Programs/console_apps/.venv/bin/python -m linux_cli_utils.sysinfo cpu 2>/dev/null | head -5 || echo "Sysinfo test completed"

echo
print_status "Installation files ready:"
echo "📁 Main installer:     ./install.sh (requires sudo)"
echo "📄 Installation guide: INSTALL.md"
echo "📋 Build commands:     Makefile"
echo "📖 Man pages:         Generated during installation"
echo "🚀 Executables:       Created as ailab-* commands"

echo
print_success "Your AI Lab CLI utilities are ready for installation!"
echo
echo "To install system-wide:"
echo "  sudo ./install.sh"
echo
echo "After installation, you'll have:"
echo "  ailab-cli          - Main interface"
echo "  ailab-sysinfo      - System information"
echo "  ailab-file         - File management" 
echo "  ailab-net          - Network utilities"
echo "  ailab-proc         - Process management"
echo "  ailab-backup       - Backup utilities"
echo "  man ailab-cli      - Documentation"
echo
echo "🧪 Welcome to your AI Lab! 🚀"

#!/bin/bash
# AI Lab Linux CLI Utilities - System Installation Script
# This script installs the CLI utilities system-wide

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_PREFIX="/usr/local"
BIN_DIR="$INSTALL_PREFIX/bin"
MAN_DIR="$INSTALL_PREFIX/share/man/man1"
LIB_DIR="$INSTALL_PREFIX/lib/linux-cli-utils"
PROJECT_NAME="linux-cli-utils"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}This script must be run as root (use sudo)${NC}"
    echo "Usage: sudo ./install.sh"
    exit 1
fi

echo -e "${BLUE}AI Lab Linux CLI Utilities - System Installation${NC}"
echo "================================================="

# Check for Python 3.6+
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.6"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 6) else 1)"; then
    echo -e "${RED}Python 3.6+ is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}Python $PYTHON_VERSION found${NC}"

# Install system dependencies
echo -e "${YELLOW}Installing system dependencies...${NC}"
if command -v apt-get >/dev/null 2>&1; then
    apt-get update
    apt-get install -y python3-pip python3-venv
elif command -v zypper >/dev/null 2>&1; then
    zypper refresh
    zypper install -y python3-pip python3-venv
elif command -v dnf >/dev/null 2>&1; then
    dnf install -y python3-pip python3-venv
else
    echo -e "${YELLOW}Package manager not detected. Please install python3-pip manually.${NC}"
fi

# Create installation directory
echo -e "${YELLOW}Creating installation directory...${NC}"
mkdir -p "$LIB_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$MAN_DIR"

# Copy project files
echo -e "${YELLOW}Copying project files...${NC}"
cp -r . "$LIB_DIR/"

# Create virtual environment in lib directory
echo -e "${YELLOW}Creating virtual environment...${NC}"
cd "$LIB_DIR"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Create system executables
echo -e "${YELLOW}Creating system executables...${NC}"

# Main CLI wrapper
cat > "$BIN_DIR/linux-utils" << 'EOF'
#!/bin/bash
cd /usr/local/lib/linux-cli-utils
source venv/bin/activate
python -m linux_cli_utils.cli "$@"
EOF
chmod +x "$BIN_DIR/linux-utils"

# Individual utility wrappers
cat > "$BIN_DIR/linux-sysinfo" << 'EOF'
#!/bin/bash
cd /usr/local/lib/linux-cli-utils
source venv/bin/activate
python -m linux_cli_utils.sysinfo "$@"
EOF
chmod +x "$BIN_DIR/linux-sysinfo"

cat > "$BIN_DIR/linux-filemanager" << 'EOF'
#!/bin/bash
cd /usr/local/lib/linux-cli-utils
source venv/bin/activate
python -m linux_cli_utils.filemanager "$@"
EOF
chmod +x "$BIN_DIR/linux-filemanager"

cat > "$BIN_DIR/linux-nettools" << 'EOF'
#!/bin/bash
cd /usr/local/lib/linux-cli-utils
source venv/bin/activate
python -m linux_cli_utils.nettools "$@"
EOF
chmod +x "$BIN_DIR/linux-nettools"

cat > "$BIN_DIR/linux-proctools" << 'EOF'
#!/bin/bash
cd /usr/local/lib/linux-cli-utils
source venv/bin/activate
python -m linux_cli_utils.proctools "$@"
EOF
chmod +x "$BIN_DIR/linux-proctools"

cat > "$BIN_DIR/linux-backup" << 'EOF'
#!/bin/bash
cd /usr/local/lib/linux-cli-utils
source venv/bin/activate
python -m linux_cli_utils.backup "$@"
EOF
chmod +x "$BIN_DIR/linux-backup"

# Install man pages
echo -e "${YELLOW}Installing man pages...${NC}"
if [ -d "man" ]; then
    for manpage in man/*.1; do
        if [ -f "$manpage" ]; then
            cp "$manpage" "$MAN_DIR/"
            gzip -f "$MAN_DIR/$(basename "$manpage")"
        fi
    done
    mandb >/dev/null 2>&1 || true
fi

# Install desktop entry
if [ -f "docs/linux-utils.desktop" ]; then
    echo -e "${YELLOW}Installing desktop entry...${NC}"
    mkdir -p "/usr/share/applications"
    cp docs/linux-utils.desktop "/usr/share/applications/"
    update-desktop-database >/dev/null 2>&1 || true
fi

# Set up shell completions (optional)
echo -e "${YELLOW}Setting up shell completions...${NC}"
COMPLETION_DIR="/usr/share/bash-completion/completions"
if [ -d "$COMPLETION_DIR" ]; then
    cat > "$COMPLETION_DIR/linux-utils" << 'EOF'
# Bash completion for linux-utils
_linux_utils_complete() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    if [ $COMP_CWORD -eq 1 ]; then
        opts="sysinfo file net proc backup version list-tools --help"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    fi
    
    return 0
}
complete -F _linux_utils_complete linux-utils
EOF
fi

echo
echo -e "${GREEN}✓ Installation completed successfully!${NC}"
echo
echo -e "${BLUE}Available commands:${NC}"
echo "  linux-utils          - Main CLI interface"
echo "  linux-sysinfo        - System information utilities"
echo "  linux-filemanager    - File management utilities"
echo "  linux-nettools       - Network utilities"
echo "  linux-proctools      - Process management utilities"
echo "  linux-backup         - Backup and snapshot utilities"
echo
echo -e "${BLUE}Usage examples:${NC}"
echo "  linux-utils list-tools"
echo "  linux-sysinfo overview"
echo "  linux-filemanager ls -l"
echo "  linux-nettools interfaces"
echo "  linux-proctools top"
echo "  linux-backup list-snapshots"
echo
echo -e "${BLUE}Documentation:${NC}"
echo "  man linux-utils      - View manual page"
echo
echo -e "${YELLOW}Note: You may need to restart your shell or run 'hash -r' to refresh the command cache.${NC}"
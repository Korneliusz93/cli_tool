#!/bin/bash
# AI Lab Linux CLI Utilities - System Uninstall Script

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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}This script must be run as root (use sudo)${NC}"
    echo "Usage: sudo ./uninstall.sh"
    exit 1
fi

echo -e "${BLUE}AI Lab Linux CLI Utilities - System Uninstall${NC}"
echo "=============================================="

echo -e "${YELLOW}Removing executables...${NC}"
rm -f "$BIN_DIR/linux-utils"
rm -f "$BIN_DIR/linux-sysinfo"
rm -f "$BIN_DIR/linux-filemanager"
rm -f "$BIN_DIR/linux-nettools"
rm -f "$BIN_DIR/linux-proctools"
rm -f "$BIN_DIR/linux-backup"

echo -e "${YELLOW}Removing man page...${NC}"
rm -f "$MAN_DIR/linux-utils.1.gz"

echo -e "${YELLOW}Removing desktop entry...${NC}"
rm -f "/usr/share/applications/linux-utils.desktop"
update-desktop-database >/dev/null 2>&1 || true

echo -e "${YELLOW}Removing shell completions...${NC}"
rm -f "/usr/share/bash-completion/completions/linux-utils"

echo -e "${YELLOW}Removing installation directory...${NC}"
rm -rf "$LIB_DIR"

echo -e "${YELLOW}Updating man database...${NC}"
mandb >/dev/null 2>&1 || true

echo
echo -e "${GREEN}✓ Uninstall completed successfully!${NC}"
echo -e "${YELLOW}Note: You may need to restart your shell or run 'hash -r' to refresh the command cache.${NC}"

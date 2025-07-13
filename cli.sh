#!/bin/bash
# Linux CLI Utilities - Quick Commands Script

PYTHON_PATH="/home/admin/Programs/console_apps/.venv/bin/python"
PROJECT_ROOT="/home/admin/Programs/console_apps"

cd "$PROJECT_ROOT"

case "$1" in
    "sysinfo")
        "$PYTHON_PATH" -m linux_cli_utils.sysinfo "${@:2}"
        ;;
    "file")
        "$PYTHON_PATH" -m linux_cli_utils.filemanager "${@:2}"
        ;;
    "net")
        "$PYTHON_PATH" -m linux_cli_utils.nettools "${@:2}"
        ;;
    "proc")
        "$PYTHON_PATH" -m linux_cli_utils.proctools "${@:2}"
        ;;
    "test")
        "$PYTHON_PATH" -m pytest tests/ -v
        ;;
    "format")
        "$PYTHON_PATH" -m black src/ tests/
        ;;
    "install")
        "$PYTHON_PATH" -m pip install -e .
        ;;
    "help"|"")
        echo "Linux CLI Utilities - Quick Commands"
        echo ""
        echo "Usage: $0 <command> [args...]"
        echo ""
        echo "Commands:"
        echo "  sysinfo [cmd]    - System information utilities"
        echo "  file [cmd]       - File management utilities"
        echo "  net [cmd]        - Network utilities"
        echo "  proc [cmd]       - Process management utilities"
        echo "  test             - Run test suite"
        echo "  format           - Format code with Black"
        echo "  install          - Install package in development mode"
        echo "  help             - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 sysinfo overview"
        echo "  $0 file ls -l"
        echo "  $0 net interfaces"
        echo "  $0 proc top -l 5"
        echo "  $0 test"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for available commands"
        exit 1
        ;;
esac

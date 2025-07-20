"""Main CLI entry point for Linux utilities."""

import typer
from rich.console import Console
from rich.table import Table

from .sysinfo import app as sysinfo_app
from .filemanager import app as filemanager_app
from .nettools import app as nettools_app
from .proctools import app as proctools_app
from .backup import app as backup_app

app = typer.Typer(
    help="Linux CLI Utilities - A collection of system administration tools"
)
console = Console()

# Add subcommands
app.add_typer(sysinfo_app, name="sysinfo", help="System information utilities")
app.add_typer(filemanager_app, name="file", help="File management utilities")
app.add_typer(nettools_app, name="net", help="Network utilities")
app.add_typer(proctools_app, name="proc", help="Process management utilities")
app.add_typer(backup_app, name="backup", help="Backup and snapshot utilities")
app.add_typer(proctools_app, name="proc", help="Process management utilities")


@app.command()
def version():
    """Show version information."""
    console.print("[bold green]Linux CLI Utilities[/bold green] v0.1.0")
    console.print("A collection of Python-based command line utilities for Linux")


@app.command()
def list_tools():
    """List all available tools."""
    table = Table(title="Available Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Description", style="magenta")

    tools = [
        ("sysinfo", "System information and hardware details"),
        ("file", "File management and organization utilities"),
        ("net", "Network monitoring and configuration tools"),
        ("proc", "Process management and monitoring utilities"),
        ("backup", "Backup and snapshot management utilities"),
    ]

    for tool, desc in tools:
        table.add_row(tool, desc)

    console.print(table)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()

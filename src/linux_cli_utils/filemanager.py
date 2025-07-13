"""File management utilities."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import stat
import time

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel

app = typer.Typer(help="File management utilities")
console = Console()


def get_file_info(path: Path) -> Dict[str, Any]:
    """Get detailed file information."""
    try:
        stat_info = path.stat()
        return {
            "size": stat_info.st_size,
            "size_human": format_size(stat_info.st_size),
            "modified": time.ctime(stat_info.st_mtime),
            "permissions": stat.filemode(stat_info.st_mode),
            "owner": stat_info.st_uid,
            "group": stat_info.st_gid,
            "is_dir": path.is_dir(),
            "is_file": path.is_file(),
            "is_symlink": path.is_symlink(),
        }
    except (OSError, PermissionError):
        return {}


def format_size(size: int) -> str:
    """Format file size in human readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def find_files(
    directory: Path,
    pattern: str = "*",
    include_hidden: bool = False,
    file_type: str = "all",
) -> List[Path]:
    """Find files matching criteria."""
    files = []

    try:
        for item in directory.rglob(pattern):
            # Skip hidden files if not requested
            if not include_hidden and any(part.startswith(".") for part in item.parts):
                continue

            # Filter by file type
            if file_type == "files" and not item.is_file():
                continue
            elif file_type == "dirs" and not item.is_dir():
                continue

            files.append(item)
    except PermissionError:
        console.print(f"[red]Permission denied accessing {directory}[/red]")

    return files


@app.command()
def ls(
    path: str = typer.Argument(".", help="Directory to list"),
    long: bool = typer.Option(False, "-l", "--long", help="Use long listing format"),
    all_files: bool = typer.Option(False, "-a", "--all", help="Show hidden files"),
    human: bool = typer.Option(
        False, "-h", "--human-readable", help="Human readable sizes"
    ),
):
    """Enhanced directory listing."""
    directory = Path(path)

    if not directory.exists():
        console.print(f"[red]Directory '{path}' does not exist[/red]")
        return

    if not directory.is_dir():
        console.print(f"[red]'{path}' is not a directory[/red]")
        return

    try:
        items = list(directory.iterdir())

        # Filter hidden files if not requested
        if not all_files:
            items = [item for item in items if not item.name.startswith(".")]

        # Sort items
        items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

        if long:
            table = Table(title=f"Directory listing: {directory}")
            table.add_column("Permissions", style="cyan")
            table.add_column("Owner", style="magenta")
            table.add_column("Group", style="yellow")
            table.add_column("Size", style="green", justify="right")
            table.add_column("Modified", style="blue")
            table.add_column("Name", style="bright_white")

            for item in items:
                info = get_file_info(item)
                if info:
                    size_str = info["size_human"] if human else str(info["size"])
                    table.add_row(
                        info["permissions"],
                        str(info["owner"]),
                        str(info["group"]),
                        size_str,
                        info["modified"],
                        (
                            f"[bold blue]{item.name}[/bold blue]"
                            if item.is_dir()
                            else item.name
                        ),
                    )

            console.print(table)
        else:
            # Simple listing
            for item in items:
                if item.is_dir():
                    console.print(f"[bold blue]{item.name}/[/bold blue]")
                else:
                    console.print(item.name)

    except PermissionError:
        console.print(f"[red]Permission denied accessing {directory}[/red]")


@app.command()
def find(
    directory: str = typer.Argument(".", help="Directory to search in"),
    pattern: str = typer.Option("*", "-p", "--pattern", help="Search pattern"),
    name: str = typer.Option(None, "-n", "--name", help="Search by name"),
    file_type: str = typer.Option(
        "all", "-t", "--type", help="File type: all, files, dirs"
    ),
    size: str = typer.Option(
        None, "-s", "--size", help="Size filter (+100M, -1G, etc)"
    ),
    hidden: bool = typer.Option(False, "--hidden", help="Include hidden files"),
):
    """Find files and directories."""
    search_dir = Path(directory)

    if not search_dir.exists():
        console.print(f"[red]Directory '{directory}' does not exist[/red]")
        return

    # Use name pattern if provided
    if name:
        pattern = f"*{name}*"

    files = find_files(search_dir, pattern, hidden, file_type)

    if not files:
        console.print("[yellow]No files found matching criteria[/yellow]")
        return

    table = Table(title=f"Search results in {search_dir}")
    table.add_column("Type", style="cyan")
    table.add_column("Size", style="green", justify="right")
    table.add_column("Modified", style="blue")
    table.add_column("Path", style="bright_white")

    for file_path in files:
        info = get_file_info(file_path)
        if info:
            file_type_str = "DIR" if info["is_dir"] else "FILE"
            table.add_row(
                file_type_str, info["size_human"], info["modified"], str(file_path)
            )

    console.print(table)
    console.print(f"\n[green]Found {len(files)} items[/green]")


@app.command()
def tree(
    path: str = typer.Argument(".", help="Directory to show tree for"),
    max_depth: int = typer.Option(3, "-d", "--depth", help="Maximum depth"),
    show_hidden: bool = typer.Option(False, "-a", "--all", help="Show hidden files"),
):
    """Show directory tree."""
    directory = Path(path)

    if not directory.exists():
        console.print(f"[red]Directory '{path}' does not exist[/red]")
        return

    if not directory.is_dir():
        console.print(f"[red]'{path}' is not a directory[/red]")
        return

    tree = Tree(f"[bold blue]{directory.name}/[/bold blue]")

    def add_to_tree(tree_node, current_path: Path, current_depth: int = 0):
        if current_depth >= max_depth:
            return

        try:
            items = list(current_path.iterdir())

            # Filter hidden files if not requested
            if not show_hidden:
                items = [item for item in items if not item.name.startswith(".")]

            # Sort items
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

            for item in items:
                if item.is_dir():
                    branch = tree_node.add(f"[bold blue]{item.name}/[/bold blue]")
                    add_to_tree(branch, item, current_depth + 1)
                else:
                    info = get_file_info(item)
                    size_str = info.get("size_human", "") if info else ""
                    tree_node.add(f"{item.name} [dim]({size_str})[/dim]")

        except PermissionError:
            tree_node.add("[red]Permission denied[/red]")

    add_to_tree(tree, directory)
    console.print(tree)


@app.command()
def du(
    path: str = typer.Argument(".", help="Directory to analyze"),
    human: bool = typer.Option(
        True, "-h", "--human-readable", help="Human readable sizes"
    ),
    summarize: bool = typer.Option(False, "-s", "--summarize", help="Show only total"),
):
    """Analyze disk usage."""
    directory = Path(path)

    if not directory.exists():
        console.print(f"[red]Directory '{path}' does not exist[/red]")
        return

    if not directory.is_dir():
        console.print(f"[red]'{path}' is not a directory[/red]")
        return

    def get_directory_size(path: Path) -> int:
        """Get total size of directory."""
        total_size = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, PermissionError):
                        continue
        except PermissionError:
            pass
        return total_size

    if summarize:
        total_size = get_directory_size(directory)
        size_str = format_size(total_size) if human else str(total_size)
        console.print(f"{size_str}\t{directory}")
    else:
        table = Table(title=f"Disk usage: {directory}")
        table.add_column("Size", style="green", justify="right")
        table.add_column("Path", style="bright_white")

        try:
            subdirs = [item for item in directory.iterdir() if item.is_dir()]
            subdirs.sort(key=lambda x: x.name.lower())

            for subdir in subdirs:
                size = get_directory_size(subdir)
                size_str = format_size(size) if human else str(size)
                table.add_row(size_str, str(subdir))

            console.print(table)

            # Show total
            total_size = get_directory_size(directory)
            total_str = format_size(total_size) if human else str(total_size)
            console.print(f"\n[bold green]Total: {total_str}[/bold green]")

        except PermissionError:
            console.print(f"[red]Permission denied accessing {directory}[/red]")


def main():
    """Main entry point for filemanager utility."""
    app()


if __name__ == "__main__":
    main()

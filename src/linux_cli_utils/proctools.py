"""Process management utilities."""

import os
import signal
from typing import Dict, List, Optional
import time

import psutil
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from linux_cli_utils.utils import run_command, format_size, format_time

app = typer.Typer(help="Process management utilities")
console = Console()


def get_process_info(pid: int) -> Optional[Dict]:
    """Get detailed information about a process."""
    try:
        process = psutil.Process(pid)
        return {
            "pid": process.pid,
            "name": process.name(),
            "status": process.status(),
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "memory_info": process.memory_info(),
            "create_time": process.create_time(),
            "cmdline": " ".join(process.cmdline()) if process.cmdline() else "",
            "username": process.username(),
            "cwd": process.cwd() if hasattr(process, "cwd") else "",
            "num_threads": process.num_threads(),
            "connections": (
                len(process.connections()) if hasattr(process, "connections") else 0
            ),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def get_top_processes(limit: int = 10, sort_by: str = "cpu") -> List[Dict]:
    """Get top processes by CPU or memory usage."""
    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent", "username"]
    ):
        try:
            proc_info = proc.info
            if proc_info["cpu_percent"] is not None:
                processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort by specified criteria
    if sort_by == "cpu":
        processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
    elif sort_by == "memory":
        processes.sort(key=lambda x: x["memory_percent"], reverse=True)

    return processes[:limit]


def kill_process(pid: int, force: bool = False) -> bool:
    """Kill a process by PID."""
    try:
        process = psutil.Process(pid)
        if force:
            process.kill()  # SIGKILL
        else:
            process.terminate()  # SIGTERM
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def find_processes(name: str) -> List[Dict]:
    """Find processes by name."""
    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent", "username"]
    ):
        try:
            if name.lower() in proc.info["name"].lower():
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes


@app.command()
def ps(
    user: str = typer.Option(None, "-u", "--user", help="Filter by username"),
    sort: str = typer.Option(
        "cpu", "-s", "--sort", help="Sort by: cpu, memory, pid, name"
    ),
    limit: int = typer.Option(20, "-l", "--limit", help="Limit number of results"),
):
    """Show running processes."""
    console.print("[bold green]Running Processes[/bold green]")

    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent", "username", "status"]
    ):
        try:
            proc_info = proc.info

            # Filter by user if specified
            if user and proc_info["username"] != user:
                continue

            processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort processes
    if sort == "cpu":
        processes.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)
    elif sort == "memory":
        processes.sort(key=lambda x: x["memory_percent"] or 0, reverse=True)
    elif sort == "pid":
        processes.sort(key=lambda x: x["pid"])
    elif sort == "name":
        processes.sort(key=lambda x: x["name"].lower())

    # Limit results
    processes = processes[:limit]

    table = Table(title="Process List")
    table.add_column("PID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("CPU %", style="green", justify="right")
    table.add_column("Memory %", style="red", justify="right")
    table.add_column("User", style="blue")
    table.add_column("Status", style="yellow")

    for proc in processes:
        table.add_row(
            str(proc["pid"]),
            proc["name"][:20],
            f"{proc['cpu_percent']:.1f}" if proc["cpu_percent"] else "0.0",
            f"{proc['memory_percent']:.1f}" if proc["memory_percent"] else "0.0",
            proc["username"][:15],
            proc["status"],
        )

    console.print(table)


@app.command()
def top(
    limit: int = typer.Option(10, "-l", "--limit", help="Number of processes to show"),
    sort_by: str = typer.Option("cpu", "-s", "--sort", help="Sort by: cpu or memory"),
):
    """Show top processes by resource usage."""
    console.print(
        f"[bold green]Top {limit} Processes by {sort_by.upper()}[/bold green]"
    )

    processes = get_top_processes(limit, sort_by)

    table = Table(title=f"Top Processes by {sort_by.upper()}")
    table.add_column("PID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("CPU %", style="green", justify="right")
    table.add_column("Memory %", style="red", justify="right")
    table.add_column("User", style="blue")

    for proc in processes:
        table.add_row(
            str(proc["pid"]),
            proc["name"][:20],
            f"{proc['cpu_percent']:.1f}",
            f"{proc['memory_percent']:.1f}",
            proc["username"][:15],
        )

    console.print(table)


@app.command()
def info(pid: int = typer.Argument(..., help="Process ID to inspect")):
    """Show detailed information about a process."""
    console.print(f"[bold green]Process Information: PID {pid}[/bold green]")

    proc_info = get_process_info(pid)

    if not proc_info:
        console.print(f"[red]Process {pid} not found or access denied[/red]")
        return

    table = Table(title=f"Process Details: {proc_info['name']}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("PID", str(proc_info["pid"]))
    table.add_row("Name", proc_info["name"])
    table.add_row("Status", proc_info["status"])
    table.add_row("CPU %", f"{proc_info['cpu_percent']:.1f}")
    table.add_row("Memory %", f"{proc_info['memory_percent']:.1f}")
    table.add_row("Memory RSS", format_size(proc_info["memory_info"].rss))
    table.add_row("Memory VMS", format_size(proc_info["memory_info"].vms))
    table.add_row("Created", format_time(proc_info["create_time"]))
    table.add_row("User", proc_info["username"])
    table.add_row("Threads", str(proc_info["num_threads"]))
    table.add_row("Connections", str(proc_info["connections"]))

    if proc_info["cwd"]:
        table.add_row("Working Dir", proc_info["cwd"])

    console.print(table)

    if proc_info["cmdline"]:
        console.print(Panel(proc_info["cmdline"], title="Command Line"))


@app.command()
def find(name: str = typer.Argument(..., help="Process name to search for")):
    """Find processes by name."""
    console.print(f"[bold green]Searching for processes matching: {name}[/bold green]")

    processes = find_processes(name)

    if not processes:
        console.print(f"[yellow]No processes found matching '{name}'[/yellow]")
        return

    table = Table(title=f"Processes matching '{name}'")
    table.add_column("PID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("CPU %", style="green", justify="right")
    table.add_column("Memory %", style="red", justify="right")
    table.add_column("User", style="blue")

    for proc in processes:
        table.add_row(
            str(proc["pid"]),
            proc["name"],
            f"{proc['cpu_percent']:.1f}" if proc["cpu_percent"] else "0.0",
            f"{proc['memory_percent']:.1f}" if proc["memory_percent"] else "0.0",
            proc["username"],
        )

    console.print(table)


@app.command()
def kill(
    pid: int = typer.Argument(..., help="Process ID to kill"),
    force: bool = typer.Option(False, "-f", "--force", help="Force kill (SIGKILL)"),
):
    """Kill a process by PID."""
    console.print(
        f"[bold yellow]Killing process {pid}{'(force)' if force else ''}[/bold yellow]"
    )

    if kill_process(pid, force):
        console.print(f"[green]Process {pid} killed successfully[/green]")
    else:
        console.print(f"[red]Failed to kill process {pid}[/red]")


@app.command()
def monitor(
    interval: int = typer.Option(
        2, "-i", "--interval", help="Update interval in seconds"
    ),
    limit: int = typer.Option(10, "-l", "--limit", help="Number of processes to show"),
):
    """Monitor top processes in real-time."""
    console.print("[bold green]Process Monitor (Press Ctrl+C to exit)[/bold green]")

    try:
        while True:
            console.clear()
            console.print(
                f"[bold green]Top {limit} Processes by CPU Usage[/bold green]"
            )
            console.print(f"Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")

            processes = get_top_processes(limit, "cpu")

            table = Table(title="Live Process Monitor")
            table.add_column("PID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("CPU %", style="green", justify="right")
            table.add_column("Memory %", style="red", justify="right")
            table.add_column("User", style="blue")

            for proc in processes:
                table.add_row(
                    str(proc["pid"]),
                    proc["name"][:20],
                    f"{proc['cpu_percent']:.1f}",
                    f"{proc['memory_percent']:.1f}",
                    proc["username"][:15],
                )

            console.print(table)
            time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/yellow]")


def main():
    """Main entry point for proctools utility."""
    app()


if __name__ == "__main__":
    main()

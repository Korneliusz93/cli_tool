"""System information utilities."""

import sys
from pathlib import Path
from typing import Dict, List, Optional

import psutil
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from linux_cli_utils.utils import run_command, format_size, format_time

app = typer.Typer(help="System information utilities")
console = Console()


def get_cpu_info() -> Dict[str, str]:
    """Get CPU information."""
    cpu_info = {}

    # Get CPU model
    cpu_model = run_command("lscpu")
    if cpu_model:
        for line in cpu_model.split("\n"):
            if line.startswith("Model name:"):
                cpu_info["model"] = line.split(":", 1)[1].strip()
            elif line.startswith("CPU(s):"):
                cpu_info["cores"] = line.split(":", 1)[1].strip()
            elif line.startswith("CPU max MHz:"):
                cpu_info["max_freq"] = line.split(":", 1)[1].strip()

    # Get CPU usage
    cpu_info["usage"] = f"{psutil.cpu_percent(interval=1):.1f}%"

    return cpu_info


def get_memory_info() -> Dict[str, str]:
    """Get memory information."""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "total": f"{memory.total / (1024**3):.1f} GB",
        "available": f"{memory.available / (1024**3):.1f} GB",
        "used": f"{memory.used / (1024**3):.1f} GB",
        "usage": f"{memory.percent:.1f}%",
        "swap_total": f"{swap.total / (1024**3):.1f} GB",
        "swap_used": f"{swap.used / (1024**3):.1f} GB",
        "swap_usage": f"{swap.percent:.1f}%",
    }


def get_disk_info() -> List[Dict[str, str]]:
    """Get disk information."""
    disks = []

    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append(
                {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype,
                    "total": f"{usage.total / (1024**3):.1f} GB",
                    "used": f"{usage.used / (1024**3):.1f} GB",
                    "free": f"{usage.free / (1024**3):.1f} GB",
                    "usage": f"{usage.percent:.1f}%",
                }
            )
        except PermissionError:
            continue

    return disks


def get_network_info() -> List[Dict[str, str]]:
    """Get network interface information."""
    interfaces = []

    for name, addrs in psutil.net_if_addrs().items():
        if name == "lo":  # Skip loopback
            continue

        interface = {"name": name, "addresses": []}
        for addr in addrs:
            if addr.family == 2:  # IPv4
                interface["addresses"].append(f"IPv4: {addr.address}")
            elif addr.family == 10:  # IPv6
                interface["addresses"].append(f"IPv6: {addr.address}")

        if interface["addresses"]:
            interfaces.append(interface)

    return interfaces


@app.command()
def overview():
    """Show system overview."""
    console.print("[bold green]System Overview[/bold green]")

    # System info
    system_info = run_command("uname -a")
    if system_info:
        console.print(Panel(system_info, title="System Information"))

    # CPU info
    cpu_info = get_cpu_info()
    if cpu_info:
        cpu_table = Table(title="CPU Information")
        cpu_table.add_column("Property", style="cyan")
        cpu_table.add_column("Value", style="magenta")

        for key, value in cpu_info.items():
            cpu_table.add_row(key.replace("_", " ").title(), value)

        console.print(cpu_table)

    # Memory info
    memory_info = get_memory_info()
    mem_table = Table(title="Memory Information")
    mem_table.add_column("Property", style="cyan")
    mem_table.add_column("Value", style="magenta")

    for key, value in memory_info.items():
        mem_table.add_row(key.replace("_", " ").title(), value)

    console.print(mem_table)


@app.command()
def cpu():
    """Show detailed CPU information."""
    console.print("[bold green]CPU Information[/bold green]")

    cpu_info = get_cpu_info()
    table = Table(title="CPU Details")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")

    for key, value in cpu_info.items():
        table.add_row(key.replace("_", " ").title(), value)

    console.print(table)


@app.command()
def memory():
    """Show memory information."""
    console.print("[bold green]Memory Information[/bold green]")

    memory_info = get_memory_info()
    table = Table(title="Memory Details")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")

    for key, value in memory_info.items():
        table.add_row(key.replace("_", " ").title(), value)

    console.print(table)


@app.command()
def disk():
    """Show disk information."""
    console.print("[bold green]Disk Information[/bold green]")

    disks = get_disk_info()
    table = Table(title="Disk Usage")
    table.add_column("Device", style="cyan")
    table.add_column("Mount Point", style="magenta")
    table.add_column("Filesystem", style="yellow")
    table.add_column("Total", style="green")
    table.add_column("Used", style="red")
    table.add_column("Free", style="blue")
    table.add_column("Usage %", style="bright_red")

    for disk in disks:
        table.add_row(
            disk["device"],
            disk["mountpoint"],
            disk["filesystem"],
            disk["total"],
            disk["used"],
            disk["free"],
            disk["usage"],
        )

    console.print(table)


@app.command()
def network():
    """Show network interface information."""
    console.print("[bold green]Network Information[/bold green]")

    interfaces = get_network_info()
    table = Table(title="Network Interfaces")
    table.add_column("Interface", style="cyan")
    table.add_column("Addresses", style="magenta")

    for interface in interfaces:
        addresses = "\n".join(interface["addresses"])
        table.add_row(interface["name"], addresses)

    console.print(table)


def main():
    """Main entry point for sysinfo utility."""
    app()


if __name__ == "__main__":
    main()

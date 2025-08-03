"""Network utilities."""

import socket
from typing import Dict, List, Optional, Tuple
import re

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from linux_cli_utils.utils import run_command, format_size, format_time

app = typer.Typer(help="Network utilities")
console = Console()


def get_network_interfaces() -> List[Dict[str, str]]:
    """Get network interface information."""
    interfaces = []

    # Use ip command to get interface info
    output = run_command("ip addr show")
    if not output:
        return interfaces

    current_interface = None
    for line in output.split("\n"):
        line = line.strip()

        # New interface
        if re.match(r"^\d+:", line):
            if current_interface:
                interfaces.append(current_interface)

            parts = line.split()
            interface_name = parts[1].rstrip(":")
            current_interface = {
                "name": interface_name,
                "state": "UP" if "UP" in line else "DOWN",
                "ipv4": "",
                "ipv6": "",
                "mac": "",
            }

        # IPv4 address
        elif "inet " in line and current_interface:
            parts = line.split()
            if len(parts) >= 2:
                current_interface["ipv4"] = parts[1]

        # IPv6 address
        elif "inet6 " in line and current_interface:
            parts = line.split()
            if len(parts) >= 2 and not parts[1].startswith("fe80"):
                current_interface["ipv6"] = parts[1]

        # MAC address
        elif "link/ether" in line and current_interface:
            parts = line.split()
            if len(parts) >= 2:
                current_interface["mac"] = parts[1]

    # Add the last interface
    if current_interface:
        interfaces.append(current_interface)

    return interfaces


def ping_host(host: str, count: int = 4) -> Dict[str, str]:
    """Ping a host and return statistics."""
    cmd = f"ping -c {count} {host}"
    output = run_command(cmd)

    if not output:
        return {"status": "failed", "error": "Host unreachable"}

    # Parse ping output
    lines = output.split("\n")
    stats = {"status": "success", "host": host}

    for line in lines:
        if "packets transmitted" in line:
            # Extract packet statistics
            parts = line.split()
            stats["transmitted"] = parts[0]
            stats["received"] = parts[3]
            stats["loss"] = parts[5]
        elif "min/avg/max" in line:
            # Extract timing statistics
            times = line.split("=")[1].strip().split("/")
            stats["min"] = times[0]
            stats["avg"] = times[1]
            stats["max"] = times[2]

    return stats


def scan_ports(host: str, ports: List[int], timeout: int = 1) -> Dict[int, str]:
    """Scan ports on a host."""
    results = {}

    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                results[port] = "open"
            else:
                results[port] = "closed"
        except socket.gaierror:
            results[port] = "error"

    return results


def get_routing_table() -> List[Dict[str, str]]:
    """Get routing table information."""
    routes = []

    output = run_command("ip route show")
    if not output:
        return routes

    for line in output.split("\n"):
        if line.strip():
            parts = line.split()
            if len(parts) >= 3:
                route = {
                    "destination": parts[0],
                    "gateway": "",
                    "interface": "",
                    "metric": "",
                }

                # Parse route details
                for i, part in enumerate(parts):
                    if part == "via" and i + 1 < len(parts):
                        route["gateway"] = parts[i + 1]
                    elif part == "dev" and i + 1 < len(parts):
                        route["interface"] = parts[i + 1]
                    elif part == "metric" and i + 1 < len(parts):
                        route["metric"] = parts[i + 1]

                routes.append(route)

    return routes


@app.command()
def interfaces():
    """Show network interfaces."""
    console.print("[bold green]Network Interfaces[/bold green]")

    interfaces = get_network_interfaces()

    table = Table(title="Network Interfaces")
    table.add_column("Interface", style="cyan")
    table.add_column("State", style="magenta")
    table.add_column("IPv4", style="green")
    table.add_column("IPv6", style="blue")
    table.add_column("MAC", style="yellow")

    for interface in interfaces:
        state_color = "green" if interface["state"] == "UP" else "red"
        table.add_row(
            interface["name"],
            f"[{state_color}]{interface['state']}[/{state_color}]",
            interface["ipv4"],
            interface["ipv6"],
            interface["mac"],
        )

    console.print(table)


@app.command()
def ping(
    host: str = typer.Argument(..., help="Host to ping"),
    count: int = typer.Option(4, "-c", "--count", help="Number of packets to send"),
):
    """Ping a host."""
    console.print(f"[bold green]Pinging {host}[/bold green]")

    stats = ping_host(host, count)

    if stats["status"] == "failed":
        console.print(
            f"[red]Failed to ping {host}: {stats.get('error', 'Unknown error')}[/red]"
        )
        return

    table = Table(title=f"Ping Statistics for {host}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Packets Transmitted", stats.get("transmitted", "N/A"))
    table.add_row("Packets Received", stats.get("received", "N/A"))
    table.add_row("Packet Loss", stats.get("loss", "N/A"))
    table.add_row("Min Time", f"{stats.get('min', 'N/A')} ms")
    table.add_row("Avg Time", f"{stats.get('avg', 'N/A')} ms")
    table.add_row("Max Time", f"{stats.get('max', 'N/A')} ms")

    console.print(table)


@app.command()
def portscan(
    host: str = typer.Argument(..., help="Host to scan"),
    ports: str = typer.Option(
        "22,80,443,8080", "-p", "--ports", help="Comma-separated ports to scan"
    ),
    timeout: int = typer.Option(1, "-t", "--timeout", help="Timeout in seconds"),
):
    """Scan ports on a host."""
    console.print(f"[bold green]Scanning ports on {host}[/bold green]")

    port_list = [int(p.strip()) for p in ports.split(",")]
    results = scan_ports(host, port_list, timeout)

    table = Table(title=f"Port Scan Results for {host}")
    table.add_column("Port", style="cyan")
    table.add_column("Status", style="magenta")

    for port, status in results.items():
        status_color = "green" if status == "open" else "red"
        table.add_row(str(port), f"[{status_color}]{status}[/{status_color}]")

    console.print(table)


@app.command()
def routes():
    """Show routing table."""
    console.print("[bold green]Routing Table[/bold green]")

    routes = get_routing_table()

    table = Table(title="Routing Table")
    table.add_column("Destination", style="cyan")
    table.add_column("Gateway", style="magenta")
    table.add_column("Interface", style="green")
    table.add_column("Metric", style="yellow")

    for route in routes:
        table.add_row(
            route["destination"],
            route["gateway"] or "-",
            route["interface"],
            route["metric"] or "-",
        )

    console.print(table)


@app.command()
def netstat():
    """Show network connections."""
    console.print("[bold green]Network Connections[/bold green]")

    # Show listening ports
    output = run_command("ss -tuln")
    if output:
        console.print(Panel(output, title="Listening Ports"))

    # Show active connections
    output = run_command("ss -tun")
    if output:
        console.print(Panel(output[:1000], title="Active Connections"))


def main():
    """Main entry point for nettools utility."""
    app()


if __name__ == "__main__":
    main()

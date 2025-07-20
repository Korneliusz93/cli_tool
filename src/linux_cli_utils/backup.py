#| Category         | Command Example(s)                                                    | Purpose/Workflow                                 | Notes/Details                                                     |
#|------------------|-----------------------------------------------------------------------|--------------------------------------------------|-------------------------------------------------------------------|
#| Snapshot Creation| snapper create --description "..."                                    | Create manual snapshot (root/default)            | Use before system changes; manual rollback point                  |
#|                  | snapper create --description "..." --cleanup-algorithm number         | Create with "number" cleanup algorithm           | Auto-retention by count                                           |
#|                  | snapper create --description "..." --cleanup-algorithm timeline       | Create with "timeline" cleanup algorithm         | Auto-retention by age/timeline                                    |
#|                  | snapper --config home create --description "..."                      | Create manual snapshot for "home" config         | Protect user data                                                 |
#|                  | snapper --config home create --description "..." 
#                                                       --cleanup-algorithm number/timeline | Home snapshot with auto-cleanup                  | Auto-managed home retention                                       |
#| Snapshot Deletion| snapper delete <id>                                                   | Delete snapshot by ID                            | Frees up space later (scheduled)                                  |
#|                  | snapper delete --sync <id>                                            | Delete & free space immediately                  | Immediate disk space recovery                                     |
#|Cleanup Assignment| snapper modify --cleanup-algorithm number <id>                       | Assign "number" cleanup to existing snapshot     | Snapshot joins retention queue                                    |
#|                  | snapper modify --cleanup-algorithm timeline <id>                      | Assign "timeline" cleanup to existing snapshot   | Auto-cleanup by age/timeline                                      |
#| Inspection       | snapper list                                                          | List all snapshots                               | Shows ID, date, description                                       |
#|                  | snapper info <id>                                                     | Show detailed info, including cleanup algorithm  | For audit and management                                          |
#|                  | snapper diff <id1> <id2>                                              | Show differences between two snapshots           | For targeted file/dir recovery                                    |
#| Configuration    | snapper get-config                                                    | Show retention settings for config               | Inspect NUMBER_LIMIT, TIMELINE_LIMIT_*                            |
#|                  | snapper -c home get-config                                            | Show retention for home config                   | Home-specific retention and cleanup settings                      |
#| Restore/Recovery | snapper -v undochange <id1>..<id2> /path/to/file                      | Restore file/directory from snapshots            | Granular, scriptable recovery                                     |
#|                  | snapper -v undochange <id1>..<id2> /                                  | Full system rollback between two snapshots       | Requires caution; not atomic                                      |
#|                  | snapper mount <id> /mnt/snap                                          | Mount snapshot for manual file recovery          | Inspect/copy files directly                                       |
#|                  | snapper umount <id>                                                   | Unmount snapshot after recovery                  | Clean up mount point                                              |
#|                  | rsync -avh /mnt/snap/path /actual/path                                | Restore files after mounting snapshot            | Efficient batch recovery                                          |

from pathlib import Path
from typing import List, Optional, Dict, Any
import stat
import time

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel

from .utils import run_command, format_size, format_time, check_command_exists

app = typer.Typer(help="Backup and snapshot utilities")
console = Console()

@app.command()
def backup(description: str = typer.Option("Manual backup snapshot", "--desc", help="Snapshot description")):
    """Create a backup using Snapper snapshots."""
    console.print("[bold green]Creating Backup Snapshot[/bold green]")

    # Check if snapper is available
    if not check_command_exists("snapper"):
        console.print("[red]Error: snapper command not found. Please install snapper.[/red]")
        raise typer.Exit(1)

    # Create a manual snapshot
    cmd = f"snapper create --description '{description}'"
    result = run_command(cmd)
    
    if result is not None:
        console.print("[bold blue]Backup snapshot created successfully![/bold blue]")
        console.print("You can now use this snapshot for recovery or inspection.")
        
        # Show latest snapshots
        list_snapshots(limit=5)
    else:
        console.print("[red]Failed to create backup snapshot[/red]")
        raise typer.Exit(1)


@app.command()
def list_snapshots(
    config: str = typer.Option("root", "--config", "-c", help="Snapper configuration"),
    limit: int = typer.Option(10, "--limit", "-l", help="Limit number of snapshots to show")
):
    """List existing snapshots."""
    console.print(f"[bold green]Snapshots for config: {config}[/bold green]")
    
    cmd = f"snapper --config {config} list"
    result = run_command(cmd)
    
    if result:
        lines = result.split('\n')
        if len(lines) > 2:  # Skip header lines
            table = Table(title="Snapshots")
            table.add_column("ID", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Date", style="green")
            table.add_column("Description", style="yellow")
            
            # Parse snapper output (skip headers)
            for line in lines[2:limit+2]:  # Skip first 2 header lines
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        snap_id = parts[0].strip()
                        snap_type = parts[1].strip()
                        snap_date = parts[2].strip()
                        snap_desc = parts[3].strip()
                        
                        table.add_row(snap_id, snap_type, snap_date, snap_desc)
            
            console.print(table)
    else:
        console.print("[red]Failed to list snapshots[/red]")


@app.command()
def snapshot_info(
    snapshot_id: int = typer.Argument(..., help="Snapshot ID"),
    config: str = typer.Option("root", "--config", "-c", help="Snapper configuration")
):
    """Show detailed information about a snapshot."""
    console.print(f"[bold green]Snapshot {snapshot_id} Information[/bold green]")
    
    cmd = f"snapper --config {config} info {snapshot_id}"
    result = run_command(cmd)
    
    if result:
        console.print(Panel(result, title=f"Snapshot {snapshot_id} Details"))
    else:
        console.print(f"[red]Snapshot {snapshot_id} not found[/red]")


@app.command()
def delete_snapshot(
    snapshot_id: int = typer.Argument(..., help="Snapshot ID to delete"),
    config: str = typer.Option("root", "--config", "-c", help="Snapper configuration"),
    sync: bool = typer.Option(False, "--sync", help="Delete synchronously (free space immediately)")
):
    """Delete a snapshot."""
    console.print(f"[bold yellow]Deleting snapshot {snapshot_id}[/bold yellow]")
    
    if typer.confirm(f"Are you sure you want to delete snapshot {snapshot_id}?"):
        sync_flag = " --sync" if sync else ""
        cmd = f"snapper --config {config} delete{sync_flag} {snapshot_id}"
        result = run_command(cmd)
        
        if result is not None:
            console.print(f"[green]Snapshot {snapshot_id} deleted successfully[/green]")
        else:
            console.print(f"[red]Failed to delete snapshot {snapshot_id}[/red]")
    else:
        console.print("Operation cancelled")


@app.command()
def mount_snapshot(
    snapshot_id: int = typer.Argument(..., help="Snapshot ID to mount"),
    mount_point: str = typer.Argument(..., help="Mount point directory"),
    config: str = typer.Option("root", "--config", "-c", help="Snapper configuration")
):
    """Mount a snapshot for file recovery."""
    console.print(f"[bold green]Mounting snapshot {snapshot_id} to {mount_point}[/bold green]")
    
    cmd = f"snapper --config {config} mount {snapshot_id} {mount_point}"
    result = run_command(cmd)
    
    if result is not None:
        console.print(f"[green]Snapshot {snapshot_id} mounted at {mount_point}[/green]")
        console.print("You can now browse and copy files from the snapshot.")
        console.print(f"Use 'umount-snapshot {snapshot_id}' when done.")
    else:
        console.print(f"[red]Failed to mount snapshot {snapshot_id}[/red]")


@app.command()
def umount_snapshot(
    snapshot_id: int = typer.Argument(..., help="Snapshot ID to unmount"),
    config: str = typer.Option("root", "--config", "-c", help="Snapper configuration")
):
    """Unmount a snapshot."""
    console.print(f"[bold green]Unmounting snapshot {snapshot_id}[/bold green]")
    
    cmd = f"snapper --config {config} umount {snapshot_id}"
    result = run_command(cmd)
    
    if result is not None:
        console.print(f"[green]Snapshot {snapshot_id} unmounted successfully[/green]")
    else:
        console.print(f"[red]Failed to unmount snapshot {snapshot_id}[/red]")


@app.command()
def restore_file(
    file_path: str = typer.Argument(..., help="Path to file/directory to restore"),
    from_snapshot: int = typer.Argument(..., help="Source snapshot ID"),
    to_snapshot: int = typer.Option(0, "--to", help="Target snapshot ID (0 for current)"),
    config: str = typer.Option("root", "--config", "-c", help="Snapper configuration")
):
    """Restore a file or directory from a snapshot."""
    console.print(f"[bold green]Restoring {file_path} from snapshot {from_snapshot}[/bold green]")
    
    if typer.confirm(f"This will restore {file_path} from snapshot {from_snapshot}. Continue?"):
        snapshot_range = f"{from_snapshot}..{to_snapshot}" if to_snapshot > 0 else str(from_snapshot)
        cmd = f"snapper --config {config} -v undochange {snapshot_range} {file_path}"
        result = run_command(cmd)
        
        if result is not None:
            console.print(f"[green]File {file_path} restored successfully[/green]")
            console.print(Panel(result, title="Restore Details"))
        else:
            console.print(f"[red]Failed to restore {file_path}[/red]")
    else:
        console.print("Restore cancelled")


def main():
    """Main entry point for backup utility."""
    app()


if __name__ == "__main__":
    main()
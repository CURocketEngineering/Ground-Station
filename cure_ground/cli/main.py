"""
CLI interface for MARTHA ground station
"""

import sys

import typer
from rich.console import Console
from rich.table import Table

from cure_ground.cli.post_flight import post_flight_flow
from cure_ground.core.functions.ping import ping_device
from cure_ground.core.functions.versions import get_versions
from cure_ground.gui.main import main as launch_gui

app = typer.Typer(help="Ground Station CLI")
console = Console()


def validate_port(port: str) -> str:
    """Validate and normalize serial port name"""
    if sys.platform.startswith("win"):
        if not port.startswith("COM"):
            port = f"COM{port}"
    else:
        if not port.startswith("/dev/"):
            port = f"/dev/{port}"
    return port


@app.command()
def gui():
    """Launch the GUI application"""
    launch_gui()


@app.command()
def ping(
    port: str = typer.Argument(..., help="Serial port (e.g., COM3 or ttyACM0)"),
    baudrate: int = typer.Option(115200, help="Serial baudrate"),
    timeout: float = typer.Option(1.0, help="Response timeout in seconds"),
    retries: int = typer.Option(3, help="Number of retry attempts"),
):
    """Test connection to MARTHA device"""
    port = validate_port(port)

    with console.status("Pinging MARTHA..."):
        success, error = ping_device(port, baudrate, timeout, retries)

    if success:
        console.print("[green]Successfully pinged MARTHA device[/green]")
    else:
        console.print(f"[red]Failed to ping MARTHA: {error}[/red]")
        raise typer.Exit(1)


@app.command()
def versions(
    port: str = typer.Argument(..., help="Serial port (e.g., COM3 or ttyACM0)"),
    baudrate: int = typer.Option(115200, help="Serial baudrate"),
    timeout: float = typer.Option(2.0, help="Response timeout in seconds"),
):
    """Get version information from MARTHA device"""
    port = validate_port(port)

    with console.status("Retrieving version information..."):
        versions_info, error = get_versions(port, baudrate, timeout)

    if versions_info is not None:
        if not versions_info:
            console.print("[yellow]No version information reported[/yellow]")
        else:
            table = Table(title="MARTHA Component Versions")
            table.add_column("Component", style="cyan")
            table.add_column("Version", style="green")

            for ver in versions_info:
                table.add_row(ver.component, ver.version)

            console.print(table)
    else:
        console.print(f"[red]Failed to get version information: {error}[/red]")
        raise typer.Exit(1)


@app.command()
def post_flight():
    """Run the post-flight data collection & processing flow"""
    post_flight_flow()


def main():
    app()


if __name__ == "__main__":
    main()

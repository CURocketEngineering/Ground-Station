# """
# CLI interface for MARTHA ground station
# """
# import typer
# from typing import Optional
# from pathlib import Path
# import sys
# from rich.console import Console
# from rich.table import Table
# from datetime import datetime

# from ..core.functions.ping import ping_device
# from ..core.functions.versions import get_versions

# app = typer.Typer(help="MARTHA Ground Station CLI")
# console = Console()

# def validate_port(port: str) -> str:
#     """Validate and normalize serial port name"""
#     if sys.platform.startswith('win'):
#         if not port.startswith('COM'):
#             port = f'COM{port}'
#     else:
#         if not port.startswith('/dev/'):
#             port = f'/dev/{port}'
#     return port

# @app.command()
# def ping(
#     port: str = typer.Argument(..., help="Serial port (e.g., COM3 or ttyACM0)"),
#     baudrate: int = typer.Option(115200, help="Serial baudrate"),
#     timeout: float = typer.Option(1.0, help="Response timeout in seconds"),
#     retries: int = typer.Option(3, help="Number of retry attempts")
# ):
#     """Test connection to MARTHA device"""
#     port = validate_port(port)
    
#     with console.status("Pinging MARTHA..."):
#         success, error = ping_device(port, baudrate, timeout, retries)
    
#     if success:
#         console.print("[green]Successfully pinged MARTHA device[/green]")
#     else:
#         console.print(f"[red]Failed to ping MARTHA: {error}[/red]")
#         raise typer.Exit(1)

# @app.command()
# def versions(
#     port: str = typer.Argument(..., help="Serial port (e.g., COM3 or ttyACM0)"),
#     baudrate: int = typer.Option(115200, help="Serial baudrate"),
#     timeout: float = typer.Option(2.0, help="Response timeout in seconds")
# ):
#     """Get version information from MARTHA device"""
#     port = validate_port(port)
    
#     with console.status("Retrieving version information..."):
#         versions_info, error = get_versions(port, baudrate, timeout)
    
#     if versions_info is not None:
#         if not versions_info:
#             console.print("[yellow]No version information reported[/yellow]")
#         else:
#             table = Table(title="MARTHA Component Versions")
#             table.add_column("Component", style="cyan")
#             table.add_column("Version", style="green")
            
#             for ver in versions_info:
#                 table.add_row(ver.component, ver.version)
            
#             console.print(table)
#     else:
#         console.print(f"[red]Failed to get version information: {error}[/red]")
#         raise typer.Exit(1)

# @app.command()
# def flash_dump(
#     port: str = typer.Argument(..., help="Serial port (e.g., COM3 or ttyACM0)"),
#     output: Path = typer.Option(
#         None,
#         help="Output CSV file path (default: flash_dump_YYYY-MM-DD_HH-MM-SS.csv)"
#     ),
#     baudrate: int = typer.Option(115200, help="Serial baudrate"),
#     timeout: float = typer.Option(10.0, help="Response timeout in seconds"),
#     generate_plots: bool = typer.Option(True, help="Generate plots from the data")
# ):
#     """Download and save flash memory contents"""
#     port = validate_port(port)
    
#     # Generate default output path if none provided
#     if output is None:
#         timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         output = Path(f"flash_dump_{timestamp}.csv")
    
#     with console.status("Downloading flash memory contents..."):
#         success, error = dump_flash(port, str(output), baudrate, timeout)
    
#     if success:
#         console.print(f"[green]Successfully saved flash dump to {output}[/green]")
        
#         if generate_plots:
#             with console.status("Generating plots..."):
#                 plot_success, plot_error = generate_graphs(str(output))
            
#             if plot_success:
#                 console.print(f"[green]Successfully generated plots in {output.with_suffix('')}/graphs/[/green]")
#             else:
#                 console.print(f"[red]Failed to generate plots: {plot_error}[/red]")
#     else:
#         console.print(f"[red]Failed to dump flash memory: {error}[/red]")
#         raise typer.Exit(1)

# def main():
#     app()

# if __name__ == "__main__":
#     main()
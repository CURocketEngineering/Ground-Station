"""
CURE Ground Station package
"""
from .core import ping_device, get_versions, dump_flash, generate_graphs
from .cli.main import main as cli_main

__version__ = "0.1.0"
__all__ = ['ping_device', 'get_versions', 'dump_flash', 'generate_graphs', 'cli_main']
"""
CURE Ground Station package
"""

from . import cli, core
from .core import get_versions, ping_device

# from .cli.main import main as cli_main

__version__ = "0.1.0"
__all__ = ["ping_device", "get_versions", "cli_main", "core", "cli"]

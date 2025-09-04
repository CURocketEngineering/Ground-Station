"""
Core functions package initialization
"""

from .ping import ping_device
from .versions import get_versions

__all__ = ["ping_device", "get_versions"]

"""
Model package for Rocket Dashboard.
Contains data models and serial communication logic.
"""

from .StatusModel import StatusModel
from .SerialConnection import SerialConnection

__all__ = ['StatusModel', 'SerialConnection']
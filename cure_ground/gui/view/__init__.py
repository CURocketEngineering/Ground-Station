"""
View package for Rocket Dashboard.
Contains UI components and presentation logic.
"""

from .MainWindow import MainWindow
from .Sidebar import Sidebar
from .StatusDisplay import StatusDisplay
from .Styles import BUTTON_STYLE, COMBO_BOX_STYLE, SIDEBAR_STYLE, get_text_style
from .TextFormatter import TextFormatter

__all__ = [
    'MainWindow', 
    'Sidebar', 
    'StatusDisplay', 
    'BUTTON_STYLE', 
    'COMBO_BOX_STYLE', 
    'SIDEBAR_STYLE', 
    'get_text_style',
    'TextFormatter'
]
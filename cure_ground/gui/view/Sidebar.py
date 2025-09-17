from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QComboBox
from PyQt6.QtGui import QFont

from view.Styles import BUTTON_STYLE, COMBO_BOX_STYLE, SIDEBAR_STYLE

class Sidebar(QWidget):
    def __init__(self, parent=None, font_family="Arial"):
        super().__init__(parent)
        self.font_family = font_family
        self.setup_ui()
        
    def setup_ui(self):
        self.setGeometry(75, 80, 250, 700)
        self.setStyleSheet(SIDEBAR_STYLE)
        self.raise_()  # Ensure sidebar appears above overlay

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 20)

        # Port dropdown
        self.port_dropdown = QComboBox()
        self.port_dropdown.setStyleSheet(COMBO_BOX_STYLE)
        layout.addWidget(self.port_dropdown)

        # Refresh button
        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.setFont(QFont(self.font_family, 20))
        self.refresh_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.refresh_button)

        # Status button
        self.status_button = QPushButton("Status")
        self.status_button.setFont(QFont(self.font_family, 20))
        self.status_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.status_button)

        layout.addStretch()
        
    def get_port_dropdown(self):
        return self.port_dropdown
        
    def get_refresh_button(self):
        return self.refresh_button
        
    def get_status_button(self):
        return self.status_button
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QComboBox, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from view.Styles import BUTTON_STYLE, COMBO_BOX_STYLE, SIDEBAR_STYLE

class Sidebar(QWidget):
    def __init__(self, parent=None, font_family="Arial"):
        super().__init__(parent)
        self.font_family = font_family
        self.setup_ui()
        
    def setup_ui(self):
        self.setGeometry(75, 80, 250, 700)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(SIDEBAR_STYLE)
        self.raise_()

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 20)

        # Data Source Selection
        source_label = QLabel("Data Source:")
        source_label.setFont(QFont(self.font_family, 14))
        source_label.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(source_label)

        self.data_source_combo = QComboBox()
        self.data_source_combo.addItems(["Select", "Radio", "Serial", "CSV"])
        self.data_source_combo.setStyleSheet(COMBO_BOX_STYLE)
        self.data_source_combo.setFont(QFont(self.font_family, 12))
        layout.addWidget(self.data_source_combo)

        # Port Selection
        port_label = QLabel("COM Port:")
        port_label.setFont(QFont(self.font_family, 14))
        port_label.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(port_label)
        self.port_label = port_label  # Store reference

        self.port_dropdown = QComboBox()
        self.port_dropdown.setStyleSheet(COMBO_BOX_STYLE)
        self.port_dropdown.setFont(QFont(self.font_family, 12))
        layout.addWidget(self.port_dropdown)

        # Refresh button
        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.setFont(QFont(self.font_family, 16))
        self.refresh_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.refresh_button)

        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFont(QFont(self.font_family, 16))
        self.connect_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.connect_button)
        
        # Status button
        self.status_button = QPushButton("Status")
        self.status_button.setFont(QFont(self.font_family, 16))
        self.status_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.status_button)

        layout.addStretch()
        
        # Connect data source change signal
        self.data_source_combo.currentTextChanged.connect(self.on_data_source_changed)
        
        # Initially set state for "Select" option
        self.on_data_source_changed("Select")
        
    def on_data_source_changed(self, source_name):
        # Show/hide and enable/disable elements based on data source
        source_lower = source_name.lower()
        
        if source_lower == "select":
            # Hide port-related elements and disable buttons
            self.port_dropdown.hide()
            self.port_label.hide()
            self.refresh_button.hide()
            self.status_button.hide()
            self.connect_button.hide()
            
        elif source_lower == "csv":
            # Hide port-related elements for CSV, but enable buttons
            self.port_dropdown.hide()
            self.port_label.hide()
            self.refresh_button.hide()
            self.status_button.show()
            self.connect_button.show()
            
        else:
            # Show port-related elements for Radio/Serial and enable buttons
            self.port_dropdown.show()
            self.port_label.show()
            self.refresh_button.show()
            self.status_button.show()
            self.connect_button.show()
        
    def get_data_source_combo(self):
        return self.data_source_combo
        
    def get_port_dropdown(self):
        return self.port_dropdown
        
    def get_refresh_button(self):
        return self.refresh_button
        
    def get_status_button(self):
        return self.status_button
        
    def get_connect_button(self):
        return self.connect_button
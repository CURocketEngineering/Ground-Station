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
        self.port_label = port_label

        self.port_dropdown = QComboBox()
        self.port_dropdown.setStyleSheet(COMBO_BOX_STYLE)
        self.port_dropdown.setFont(QFont(self.font_family, 12))
        layout.addWidget(self.port_dropdown)

        # Refresh button
        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.setFont(QFont(self.font_family, 16))
        self.refresh_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.refresh_button)

        # Connect/Status button (merged functionality)
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFont(QFont(self.font_family, 16))
        self.connect_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.connect_button)

        # Add spacer to push control buttons to bottom
        layout.addStretch()

        # Control buttons (initially hidden, shown after connection)
        self.live_update_button = QPushButton("Start Streaming")
        self.live_update_button.setFont(QFont(self.font_family, 14))
        self.live_update_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.live_update_button)
        self.live_update_button.hide()

        self.graph_button = QPushButton("Show Graph")
        self.graph_button.setFont(QFont(self.font_family, 14))
        self.graph_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.graph_button)
        self.graph_button.hide()

        self.clear_plm_button = QPushButton("Clear PLM")
        self.clear_plm_button.setFont(QFont(self.font_family, 14))
        self.clear_plm_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.clear_plm_button)
        self.clear_plm_button.hide()
        
        # Connect data source change signal
        self.data_source_combo.currentTextChanged.connect(self.on_data_source_changed)
        
        # Initially set state for "Select" option
        self.on_data_source_changed("Select")
        
    def on_data_source_changed(self, source_name):
        source_lower = source_name.lower()
        
        if source_lower == "select":
            self.port_dropdown.hide()
            self.port_label.hide()
            self.refresh_button.hide()
            self.connect_button.hide()
            self.hide_control_buttons()
        elif source_lower == "csv":
            self.port_dropdown.hide()
            self.port_label.hide()
            self.refresh_button.hide()
            self.connect_button.show()
            self.hide_control_buttons()
        else:
            self.port_dropdown.show()
            self.port_label.show()
            self.refresh_button.show()
            self.connect_button.show()
            self.hide_control_buttons()

    def show_control_buttons(self):
        # Show the control buttons at the bottom of the sidebar
        self.live_update_button.show()
        self.graph_button.show()
        self.clear_plm_button.show()

    def hide_control_buttons(self):
        # Hide the control buttons
        self.live_update_button.hide()
        self.graph_button.hide()
        self.clear_plm_button.hide()

    def update_connect_button_text(self, text):
        # Update the connect button text
        self.connect_button.setText(text)
        
    def get_data_source_combo(self):
        return self.data_source_combo
        
    def get_port_dropdown(self):
        return self.port_dropdown
        
    def get_refresh_button(self):
        return self.refresh_button
        
    def get_connect_button(self):
        return self.connect_button

    def get_live_update_button(self):
        return self.live_update_button

    def get_graph_button(self):
        return self.graph_button

    def get_clear_plm_button(self):
        return self.clear_plm_button
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from model.StatusModel import StatusModel
from model.SerialConnection import SerialConnection
from view.TextFormatter import TextFormatter

class DashboardController:
    def __init__(self, view):
        self.view = view
        self.model = StatusModel()
        self.serial_connection = SerialConnection()
        self.text_formatter = TextFormatter()
        self.streaming = False
        self.timer = QTimer()
        
        self.setup_connections()
        self.refresh_ports()
        
    def setup_connections(self):
        # Connect sidebar signals
        sidebar = self.view.get_sidebar()
        sidebar.get_refresh_button().clicked.connect(self.refresh_ports)
        sidebar.get_status_button().clicked.connect(self.show_status)
        
        # Connect status display signals
        status_display = self.view.get_status_display()
        status_display.update_button.clicked.connect(self.toggle_streaming)
        status_display.clear_button.clicked.connect(self.clear_plm)
        
        # Connect timer
        self.timer.timeout.connect(self.update_status)
        
    def refresh_ports(self):
        ports = self.serial_connection.get_available_ports()
        dropdown = self.view.get_sidebar().get_port_dropdown()
        dropdown.clear()
        dropdown.addItems(ports)
        
    def show_status(self):
        status_display = self.view.get_status_display()
        status_display.show_text()
        status_display.show_buttons()
        self.update_status()
        
    def toggle_streaming(self):
        status_display = self.view.get_status_display()
        
        if self.streaming:
            self.timer.stop()
            status_display.update_button.setText("Start Updating")
        else:
            self.timer.start(1000)
            status_display.update_button.setText("Stop Updating")
            
        self.streaming = not self.streaming
        
    def clear_plm(self):
        dropdown = self.view.get_sidebar().get_port_dropdown()
        selected_port = dropdown.currentText()
        
        if selected_port != "No Ports Available":
            if self.serial_connection.connect(selected_port):
                self.serial_connection.send_command("clear_plm")
                self.serial_connection.disconnect()
                QMessageBox.information(self.view, "", "Please reboot the board", QMessageBox.StandardButton.Ok)
                
    def update_status(self):
        dropdown = self.view.get_sidebar().get_port_dropdown()
        selected_port = dropdown.currentText()
        
        if selected_port == "No Ports Available":
            return
            
        if self.serial_connection.connect(selected_port):
            # Clear buffer
            self.serial_connection.clear_buffer()
            
            # Send status command and read response
            self.serial_connection.send_command("getstatus")
            response = self.serial_connection.read_response()
            
            # Parse and update model
            status_data = self.model.parse_status_data(response)
            self.model.update_status(status_data)
            
            # Update view
            left_text = self.text_formatter.get_left_column_text(status_data)
            right_text = self.text_formatter.get_right_column_text(status_data)
            
            status_display = self.view.get_status_display()
            status_display.update_text(left_text, right_text)
            
            self.serial_connection.disconnect()
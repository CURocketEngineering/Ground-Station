# control/DashboardController.py
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from model.StatusModel import StatusModel
from model.SerialConnection import SerialConnection
from model.DataSource import DataSource
from model.CSVDataSource import CSVDataSource
from view.TextFormatter import TextFormatter
from view.TextFormatterCSV import TextFormatterCSV

class DashboardController:
    def __init__(self, view):
        self.view = view
        self.model = StatusModel()
        self.serial_connection = SerialConnection()
        self.text_formatter = TextFormatter()
        self.text_formatter_csv = TextFormatterCSV()
        self.streaming = False
        self.timer = QTimer()
        self.current_data_source = None
        
        # Configuration - easily switch between data sources
        self.use_csv_mock_data = True  # Set to False for real serial data
        self.csv_file_path = "resources/OldData.csv"
        
        self.setup_connections()
        self.setup_data_source()
        self.refresh_ports()
        
    def setup_data_source(self):
        # Set up the appropriate data source based on configuration
        if self.use_csv_mock_data:
            # Use CSV mock data
            csv_source = CSVDataSource(self.csv_file_path, playback_speed=2.0)
            if csv_source.connect():
                self.current_data_source = csv_source
                self.model.set_data_source(csv_source)
            else:
                # Fall back to serial
                self.current_data_source = self.serial_connection
        else:
            # Use real serial data
            self.current_data_source = self.serial_connection
        
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
        self.update_status()  # Get initial data
        
    def toggle_streaming(self):
        status_display = self.view.get_status_display()
        
        if self.streaming:
            self.timer.stop()
            status_display.update_button.setText("Start Streaming")
        else:
            self.timer.start(500)  # Update every 500ms for smoother streaming
            status_display.update_button.setText("Stop Streaming")
            
        self.streaming = not self.streaming
        
    def clear_plm(self):
        if isinstance(self.current_data_source, SerialConnection):
            dropdown = self.view.get_sidebar().get_port_dropdown()
            selected_port = dropdown.currentText()
            
            if selected_port != "No Ports Available":
                if self.serial_connection.connect(selected_port):
                    self.serial_connection.send_command("clear_plm")
                    self.serial_connection.disconnect()
                    QMessageBox.information(self.view, "", "Please reboot the board", QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(self.view, "Info", "Clear PLM only works with serial connection", QMessageBox.StandardButton.Ok)
                
    def update_status(self):
        if self.use_csv_mock_data:
            self.update_from_csv()
        else:
            self.update_from_serial()
            
    def update_from_csv(self):
        # Update status from CSV data source
        if self.model.update_from_data_source():
            status_data = self.model.get_all_data()
            
            # Update view
            left_text = self.text_formatter_csv.get_left_column_text(status_data)
            right_text = self.text_formatter_csv.get_right_column_text(status_data)
            
            status_display = self.view.get_status_display()
            status_display.update_text(left_text, right_text)
            
    def update_from_serial(self):
        # Update status from serial connection
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
    
    def switch_to_serial_mode(self):
        # Switch to using real serial data
        self.use_csv_mock_data = False
        self.current_data_source = self.serial_connection
        self.model.set_data_source(None)  # Clear CSV data source
        print("Switched to serial data mode")
    
    def switch_to_csv_mode(self, csv_file_path: str = None):
        # Switch to using CSV data
        self.use_csv_mock_data = True
        if csv_file_path:
            self.csv_file_path = csv_file_path
            
        csv_source = CSVDataSource(self.csv_file_path, playback_speed=2.0)
        if csv_source.connect():
            self.current_data_source = csv_source
            self.model.set_data_source(csv_source)
            print("Switched to CSV data mode")
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox, QLabel

from data_sources import DataSourceFactory
from model.StatusModel import StatusModel
from view.TextFormatter import TextFormatter
from view.TextFormatterCSV import TextFormatterCSV

class DashboardController:
    def __init__(self, view):
        self.view = view
        self.model = StatusModel()
        self.text_formatter = TextFormatter()
        self.text_formatter_csv = TextFormatterCSV()
        self.streaming = False
        self.timer = QTimer()
        self.current_data_source = None
        self.connected = False
        
        # Configuration
        self.csv_file_path = "resources/OldData.csv"
        
        self.setup_connections()
        self.refresh_ports()
        
    def setup_connections(self):
        # Connect UI signals
        sidebar = self.view.get_sidebar()
        
        # Connect data source selection
        sidebar.get_data_source_combo().currentTextChanged.connect(self.on_data_source_changed)
        
        # Connect port refresh
        sidebar.get_refresh_button().clicked.connect(self.refresh_ports)
        
        # Connect status button
        sidebar.get_status_button().clicked.connect(self.show_status)
        
        # Connect connect/disconnect button
        sidebar.get_connect_button().clicked.connect(self.toggle_connection)
        
        # Connect status display signals
        status_display = self.view.get_status_display()
        status_display.update_button.clicked.connect(self.toggle_streaming)
        status_display.clear_button.clicked.connect(self.clear_plm)
        
        # Connect timer
        self.timer.timeout.connect(self.update_status)
        
    def get_current_data_source_type(self):
        # Get the currently selected data source type
        sidebar = self.view.get_sidebar()
        return sidebar.get_data_source_combo().currentText().lower()
        
    def get_selected_port(self):
        # Get the currently selected port
        sidebar = self.view.get_sidebar()
        port_text = sidebar.get_port_dropdown().currentText()
        # Remove any additional labels like "(Radio)"
        return port_text.split(' (')[0] if ' (' in port_text else port_text
        
    def refresh_ports(self):
        # Refresh available COM ports
        # Create a temporary serial source to get ports
        from data_sources import SerialDataSource
        temp_source = SerialDataSource()
        all_ports = temp_source.get_available_ports()
        
        # Filter out "No Ports Available"
        available_ports = [p for p in all_ports if p != "No Ports Available"]
        
        # Detect which ports have radios
        radio_ports = DataSourceFactory.detect_radio_ports()
        
        dropdown = self.view.get_sidebar().get_port_dropdown()
        dropdown.clear()
        
        if not available_ports:
            dropdown.addItem("No ports available")
        else:
            # Add ports with radio identification
            for port in available_ports:
                if port in radio_ports:
                    dropdown.addItem(f"{port} (Radio)")
                else:
                    dropdown.addItem(port)
        
    def on_data_source_changed(self, source_name):
        # Handle data source selection change
        source_name = source_name.lower()
        
        # Update UI based on selection
        sidebar = self.view.get_sidebar()
        if source_name == "csv":
            sidebar.get_port_dropdown().hide()
            # Hide the COM Port label
            for i in range(sidebar.layout().count()):
                widget = sidebar.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and widget.text() == "COM Port:":
                    widget.hide()
        else:
            sidebar.get_port_dropdown().show()
            # Show the COM Port label
            for i in range(sidebar.layout().count()):
                widget = sidebar.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and widget.text() == "COM Port:":
                    widget.show()
            
            # Refresh ports when switching to serial/radio
            self.refresh_ports()
        
        # Disconnect if currently connected to a different source
        if self.connected:
            self.disconnect()
            
        # Update connect button text
        sidebar.get_connect_button().setText("Connect")
        
    def toggle_connection(self):
        # Connect or disconnect from the selected data source
        if self.connected:
            self.disconnect()
        else:
            self.connect()
            
    def connect(self):
        # Connect to the selected data source
        try:
            source_type = self.get_current_data_source_type()
            
            # Create the appropriate data source
            if source_type == "csv":
                self.current_data_source = DataSourceFactory.create_data_source(
                    'csv', 
                    csv_file_path=self.csv_file_path
                )
                # For CSV, we need to call connect() without parameters
                if not self.current_data_source.connect():
                    print("CSV connection failed")
                    QMessageBox.warning(self.view, "Connection Error", 
                                    f"Failed to connect to CSV file: {self.csv_file_path}")
                    return
            else:
                # For serial/radio, get the selected port
                selected_port = self.get_selected_port()
                if selected_port == "No ports available":
                    QMessageBox.warning(self.view, "Connection Error", 
                                    "No COM ports available. Please check your connections.")
                    return
                
                self.current_data_source = DataSourceFactory.create_data_source(
                    source_type,
                    csv_file_path=self.csv_file_path
                )
                
                # Connect to specific port
                if not self.current_data_source.connect(selected_port):
                    QMessageBox.warning(self.view, "Connection Error", 
                                    f"Failed to connect to {selected_port}")
                    return
            
            # Set up the model and update UI
            self.model.set_data_source(self.current_data_source)
            self.connected = True
            
            # Update UI
            sidebar = self.view.get_sidebar()
            sidebar.get_connect_button().setText("Disconnect")
            sidebar.get_data_source_combo().setEnabled(False)
            sidebar.get_port_dropdown().setEnabled(False)
            
            # Show status display
            self.show_status()
            
            print(f"Connected to {source_type} data source")
            
        except Exception as e:
            print(f"Connection error: {e}")
            QMessageBox.critical(self.view, "Connection Error", 
                            f"Failed to connect: {str(e)}")            
    def disconnect(self):
        # Disconnect from the current data source
        if self.current_data_source:
            self.current_data_source.disconnect()
        
        # Stop streaming if active
        if self.streaming:
            self.toggle_streaming()
            
        # Update UI
        sidebar = self.view.get_sidebar()
        sidebar.get_connect_button().setText("Connect")
        sidebar.get_data_source_combo().setEnabled(True)
        sidebar.get_port_dropdown().setEnabled(True)
        
        # Hide status display
        status_display = self.view.get_status_display()
        status_display.hide_all()
        
        self.connected = False
        self.current_data_source = None
        print("Disconnected from data source")
        
    def show_status(self):
        # Show the status display
        if not self.connected:
            QMessageBox.information(self.view, "Not Connected", 
                                  "Please connect to a data source first.")
            return
            
        status_display = self.view.get_status_display()
        status_display.show_text()
        status_display.show_buttons()
        self.update_status()  # Get initial data
        
    def toggle_streaming(self):
        # Start or stop live data streaming
        if not self.connected:
            QMessageBox.information(self.view, "Not Connected", 
                                  "Please connect to a data source first.")
            return
            
        status_display = self.view.get_status_display()
        
        if self.streaming:
            self.timer.stop()
            status_display.update_button.setText("Start Streaming")
        else:
            self.timer.start(500)  # Update every 500ms
            status_display.update_button.setText("Stop Streaming")
            
        self.streaming = not self.streaming
        
    def update_status(self):
        # Update status from current data source
        if not self.connected or not self.current_data_source:
            print("Not connected or no data source")
            return
            
        if self.model.update_from_data_source():
            status_data = self.model.get_all_data()
            
            # Choose appropriate formatter
            source_type = self.get_current_data_source_type()
            
            if source_type in ['csv', 'radio']:
                left_text = self.text_formatter_csv.get_left_column_text(status_data)
                right_text = self.text_formatter_csv.get_right_column_text(status_data)
            else:
                left_text = self.text_formatter.get_left_column_text(status_data)
                right_text = self.text_formatter.get_right_column_text(status_data)
            
            # Update view
            status_display = self.view.get_status_display()
            status_display.update_text(left_text, right_text)
            print("Display updated")
        else:
            print("Failed to update from data source")
    
    def clear_plm(self):
        # Clear PLM - only works with serial-like sources
        if not self.connected:
            QMessageBox.information(self.view, "Not Connected", 
                                  "Please connect to a data source first.")
            return
            
        if hasattr(self.current_data_source, 'send_command'):
            self.current_data_source.send_command("clear_plm")
            QMessageBox.information(self.view, "Clear PLM", 
                                  "Please reboot the board", QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(self.view, "Not Supported", 
                                  "Clear PLM only works with serial connections", 
                                  QMessageBox.StandardButton.Ok)
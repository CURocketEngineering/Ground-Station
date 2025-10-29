from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox, QLabel

from data_sources import DataSourceFactory
from model.StatusModel import StatusModel
from view.TextFormatter import TextFormatter
from view.TextFormatterCSV import TextFormatterCSV
from view.AltitudeGraph import AltitudeGraph

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
        self.altitude_graph = None
        self.graph_visible = False
        
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
        
        # Connect connect/status button (merged functionality)
        sidebar.get_connect_button().clicked.connect(self.toggle_connection_status)
        
        # Connect control buttons in sidebar
        sidebar.get_live_update_button().clicked.connect(self.toggle_streaming)
        sidebar.get_graph_button().clicked.connect(self.toggle_graph)
        sidebar.get_clear_plm_button().clicked.connect(self.clear_plm)
        
        # Connect timer
        self.timer.timeout.connect(self.update_status)
        
    def toggle_connection_status(self):
        # Handle both connection and status display in one button
        if not self.connected:
            # Connect and show status
            self.connect_and_show_status()
        else:
            # Disconnect and hide status
            self.disconnect_and_hide()
            
    def connect_and_show_status(self):
        # Connect to data source and immediately show status
        if self.connect():  # Your existing connect method
            # Show status display after successful connection
            status_display = self.view.get_status_display()
            status_display.show_text()
            self.update_status()  # Get initial data
            
            # Show control buttons in sidebar
            sidebar = self.view.get_sidebar()
            sidebar.show_control_buttons()
            
            # Update button text to show it can disconnect
            sidebar.update_connect_button_text("Disconnect")
            
    def disconnect_and_hide(self):
        # Disconnect and hide status display
        self.disconnect()  # Your existing disconnect method
        
        # Hide control buttons in sidebar
        sidebar = self.view.get_sidebar()
        sidebar.hide_control_buttons()
        
        # Update button text back to connect
        sidebar.update_connect_button_text("Connect")
    
    def toggle_streaming(self):
        if not self.connected:
            QMessageBox.information(self.view, "Not Connected", 
                                  "Please connect to a data source first.")
            return
            
        sidebar = self.view.get_sidebar()
        
        if self.streaming:
            self.timer.stop()
            sidebar.get_live_update_button().setText("Start Streaming")
        else:
            self.timer.start(20)
            sidebar.get_live_update_button().setText("Stop Streaming")
            
        self.streaming = not self.streaming
        
    def toggle_graph(self):
        # Toggle graph visibility
        self.graph_visible = not self.graph_visible
        
        if self.graph_visible:
            self.ensure_graph_initialized()
            self.view.get_sidebar().get_graph_button().setText("Hide Graph")
        else:
            self.view.toggle_graph_visibility(False)
            self.view.get_sidebar().get_graph_button().setText("Show Graph")
            
    def get_current_data_source_type(self):
        sidebar = self.view.get_sidebar()
        return sidebar.get_data_source_combo().currentText().lower()
        
    def get_selected_port(self):
        sidebar = self.view.get_sidebar()
        port_text = sidebar.get_port_dropdown().currentText()
        return port_text.split(' (')[0] if ' (' in port_text else port_text
        
    def refresh_ports(self):
        from data_sources import SerialDataSource
        temp_source = SerialDataSource()
        all_ports = temp_source.get_available_ports()
        
        available_ports = [p for p in all_ports if p != "No Ports Available"]
        radio_ports = DataSourceFactory.detect_radio_ports()
        
        dropdown = self.view.get_sidebar().get_port_dropdown()
        dropdown.clear()
        
        if not available_ports:
            dropdown.addItem("No ports available")
        else:
            for port in available_ports:
                if port in radio_ports:
                    dropdown.addItem(f"{port} (Radio)")
                else:
                    dropdown.addItem(port)
        
    def on_data_source_changed(self, source_name):
        source_name = source_name.lower()
        
        sidebar = self.view.get_sidebar()
        if source_name == "csv":
            sidebar.get_port_dropdown().hide()
            for i in range(sidebar.layout().count()):
                widget = sidebar.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and widget.text() == "COM Port:":
                    widget.hide()
        else:
            sidebar.get_port_dropdown().show()
            for i in range(sidebar.layout().count()):
                widget = sidebar.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and widget.text() == "COM Port:":
                    widget.show()
            
            self.refresh_ports()
        
        if self.connected:
            self.disconnect_and_hide()
            
        # Update button text based on connection state
        sidebar.update_connect_button_text("Connect")
        
    def connect(self):
        try:
            source_type = self.get_current_data_source_type()
            
            if source_type == "csv":
                self.current_data_source = DataSourceFactory.create_data_source(
                    'csv', 
                    csv_file_path=self.csv_file_path
                )
                if not self.current_data_source.connect():
                    print("CSV connection failed")
                    QMessageBox.warning(self.view, "Connection Error", 
                                    f"Failed to connect to CSV file: {self.csv_file_path}")
                    return False
            else:
                selected_port = self.get_selected_port()
                if selected_port == "No ports available":
                    QMessageBox.warning(self.view, "Connection Error", 
                                    "No COM ports available. Please check your connections.")
                    return False
                
                self.current_data_source = DataSourceFactory.create_data_source(
                    source_type,
                    csv_file_path=self.csv_file_path
                )
                
                if not self.current_data_source.connect(selected_port):
                    QMessageBox.warning(self.view, "Connection Error", 
                                    f"Failed to connect to {selected_port}")
                    return False
            
            self.model.set_data_source(self.current_data_source)
            self.connected = True
            
            # Update UI (but don't show status yet - that happens in connect_and_show_status)
            sidebar = self.view.get_sidebar()
            sidebar.get_data_source_combo().setEnabled(False)
            sidebar.get_port_dropdown().setEnabled(False)
            
            print(f"Connected to {source_type} data source")
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            QMessageBox.critical(self.view, "Connection Error", 
                            f"Failed to connect: {str(e)}")
            return False
            
    def disconnect(self):
        if self.current_data_source:
            self.current_data_source.disconnect()
        
        if self.streaming:
            self.toggle_streaming()
            
        if self.altitude_graph:
            self.altitude_graph.clear_graph()
            
        # Hide graph
        self.view.toggle_graph_visibility(False)
        self.graph_visible = False
            
        sidebar = self.view.get_sidebar()
        sidebar.get_data_source_combo().setEnabled(True)
        sidebar.get_port_dropdown().setEnabled(True)
        
        status_display = self.view.get_status_display()
        status_display.hide_all()
        
        self.connected = False
        self.current_data_source = None
        print("Disconnected from data source")
        
    def update_status(self):
        if not self.connected or not self.current_data_source:
            print("Not connected or no data source")
            return
            
        if self.model.update_from_data_source():
            status_data = self.model.get_all_data()
            
            source_type = self.get_current_data_source_type()
            
            if source_type in ['csv', 'radio']:
                left_text = self.text_formatter_csv.get_left_column_text(status_data)
                right_text = self.text_formatter_csv.get_right_column_text(status_data)
            else:
                left_text = self.text_formatter.get_left_column_text(status_data)
                right_text = self.text_formatter.get_right_column_text(status_data)
            
            status_display = self.view.get_status_display()
            status_display.update_text(left_text, right_text)
    
    def clear_plm(self):
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
    
    def ensure_graph_initialized(self):
        # Initialize the graph if not already done
        if self.altitude_graph is None:
            self.altitude_graph = AltitudeGraph(self.model, self.view.font_family, self.view)
            self.view.set_altitude_graph(self.altitude_graph)
        
        # Show the graph
        self.view.toggle_graph_visibility(True)
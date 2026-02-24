import time
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from cure_ground.data_sources.DataSourceFactory import DataSourceFactory
from cure_ground.gui.model.StatusModel import StatusModel
from cure_ground.gui.view import MainWindow
from cure_ground.gui.view.OrientationVisual import OrientationView
from cure_ground.gui.view.Graphs import MergedGraph
from cure_ground.gui.view.TextFormatter import TextFormatter
from cure_ground.gui.view.TextFormatterCSV import TextFormatterCSV
from cure_ground.gui.view.TextFormatterRadio import TextFormatterRadio


class DashboardController:
    def __init__(self, view):
        self.view: MainWindow = view
        self.model = StatusModel()
        self.text_formatter = TextFormatter()
        self.text_formatter_csv = TextFormatterCSV()
        self.text_formatter_radio = TextFormatterRadio()
        self.streaming = False
        self.timer = QTimer()
        self.current_data_source = None
        self.connected = False
        self.graph_visible = False
        self._last_text_update = 0

        # Graphs
        self.merged_graph = None
        self.orientation_visual = None

        # CSV path only used for CSV sources
        self.csv_file_path = "cure_ground/gui/resources/OldData.csv"

        self.setup_connections()
        self.refresh_ports()

    # --------------------- SETUP ---------------------
    def setup_connections(self):
        sidebar = self.view.get_sidebar()
        sidebar.get_data_source_combo().currentTextChanged.connect(
            self.on_data_source_changed
        )
        sidebar.get_refresh_button().clicked.connect(self.refresh_ports)
        sidebar.get_connect_button().clicked.connect(self.toggle_connection_status)
        sidebar.get_live_update_button().clicked.connect(self.toggle_streaming)
        sidebar.get_graph_button().clicked.connect(self.toggle_graph)
        sidebar.get_clear_plm_button().clicked.connect(self.clear_plm)
        self.timer.timeout.connect(self.update_status)
        sidebar.get_clear_graphs_button().clicked.connect(self.clear_graphs)

    # --------------------- CONNECTION HANDLING ---------------------
    def toggle_connection_status(self):
        if not self.connected:
            self.connect_and_show_status()
        else:
            self.disconnect_and_hide()

    def connect_and_show_status(self):
        if self.connect():
            self.view.get_status_display().show_text()
            self.update_status()
            sidebar = self.view.get_sidebar()
            sidebar.show_control_buttons()
            sidebar.update_connect_button_text("Disconnect")

    def disconnect_and_hide(self):
        self.disconnect()
        sidebar = self.view.get_sidebar()
        sidebar.hide_control_buttons()
        sidebar.update_connect_button_text("Connect")

    def connect(self):
        try:
            source_type = self.get_current_data_source_type()

            if source_type == "csv":
                self.current_data_source = DataSourceFactory.create_data_source(
                    "csv", csv_file_path=self.csv_file_path
                )

                if not self.current_data_source.connect():
                    QMessageBox.warning(
                        self.view,
                        "Connection Error",
                        f"Failed to connect to CSV file: {self.csv_file_path}",
                    )
                    return False

            elif source_type == "radio":
                selected_port = self.get_selected_port()
                if selected_port == "No ports available":
                    QMessageBox.warning(
                        self.view,
                        "Connection Error",
                        "No COM ports available. Please check your connections.",
                    )
                    return False

                self.current_data_source = DataSourceFactory.create_data_source(
                    "radio", port=selected_port
                )

                if not self.current_data_source.connect():
                    QMessageBox.warning(
                        self.view,
                        "Connection Error",
                        f"Failed to connect to {selected_port}",
                    )
                    return False
            else:
                QMessageBox.warning(
                    self.view, "Connection Error", f"Unknown data source: {source_type}"
                )
                return False

            self.model.set_data_source(self.current_data_source)
            # use current time mm-dd-yy_hh-mm-ss format
            self.model.set_local_save_path(
                f"data_{time.strftime('%m-%d-%y_%H-%M-%S')}.csv"
            )
            self.connected = True
            sidebar = self.view.get_sidebar()
            sidebar.get_data_source_combo().setEnabled(False)
            sidebar.get_port_dropdown().setEnabled(False)
            print(f"Connected to {source_type} data source")
            return True

        except Exception as e:
            print(f"Connection error: {e}")
            QMessageBox.critical(
                self.view, "Connection Error", f"Failed to connect: {str(e)}"
            )
            return False

    def disconnect(self):
        if self.current_data_source:
            self.current_data_source.disconnect()
        if self.streaming:
            self.toggle_streaming()
        if self.merged_graph:
            self.merged_graph.clear_graph()

        self.view.toggle_graph_visual_visibility(False)
        self.graph_visible = False

        sidebar = self.view.get_sidebar()
        sidebar.get_data_source_combo().setEnabled(True)
        sidebar.get_port_dropdown().setEnabled(True)
        self.view.get_status_display().hide_all()

        self.connected = False
        self.current_data_source = None
        print("Disconnected from data source")

    # --------------------- STREAMING ---------------------
    def toggle_streaming(self):
        if not self.connected:
            QMessageBox.information(
                self.view, "Not Connected", "Please connect to a data source first."
            )
            return

        sidebar = self.view.get_sidebar()
        if self.streaming:
            self.timer.stop()
            sidebar.get_live_update_button().setText("Start Streaming")
        else:
            self.timer.start(50)
            sidebar.get_live_update_button().setText("Stop Streaming")
        self.streaming = not self.streaming

    # --------------------- GRAPH HANDLING ---------------------
    def toggle_graph(self):
        self.graph_visible = not self.graph_visible
        if self.graph_visible:
            self.ensure_graphs_initialized()
            self.view.get_sidebar().get_graph_button().setText("Hide Graphs")
        else:
            self.view.toggle_graph_visual_visibility(False)
            self.view.get_sidebar().get_graph_button().setText("Show Graphs")

    def ensure_graphs_initialized(self):
        # Orientation
        if self.orientation_visual is None:
            self.orientation_visual = OrientationView(status_model=self.model)
            self.view.set_orientation_visual(self.orientation_visual)

        # Combined graph
        if self.merged_graph is None:
            self.merged_graph = MergedGraph()
            self.view.set_merged_graph(self.merged_graph)

        # Attach model every time
        self.merged_graph.set_model(self.model)

        # Show them
        self.view.toggle_graph_visual_visibility(True)

        # Force layout refresh
        self.view.resizeEvent(None)

    # --------------------- STATUS UPDATES ---------------------
    def update_status(self):
        if not self.connected or not self.current_data_source:
            return

        if self.model.update_from_data_source():
            status_data = self.model.get_all_data()
            source_type = self.get_current_data_source_type()

            if source_type == "csv":
                formatter = self.text_formatter_csv
            elif source_type == "radio":
                formatter = self.text_formatter_radio
            else:
                formatter = self.text_formatter

            now = time.time()
            if now - self._last_text_update > 0.05:  # update text at ~20 FPS max
                # Round all numbers in status data to 2 decimal places for display
                for key, value in status_data.items():
                    if type(value) in [int, float]:
                        status_data[key] = f"{value:.2f}"
                left_text = formatter.get_left_column_text(status_data)
                right_text = formatter.get_right_column_text(status_data)
                self.view.get_status_display().update_text(left_text, right_text)
                self._last_text_update = now

            # === NEW: Update packet loss bar ===
            # Instead of loss_ratio
            retention_ratio = self.model.get_packet_retention_ratio()  # 0.0 - 1.0
            self.view.get_packet_loss_indicator().set_packet_loss(retention_ratio)


    # --------------------- HELPERS ---------------------
    def clear_plm(self):
        if not self.connected:
            QMessageBox.information(
                self.view, "Not Connected", "Please connect to a data source first."
            )
            return
        if self.current_data_source is None:
            QMessageBox.information(
                self.view,
                "No Data Source",
                "No data source is currently connected. We need a Serial connection to clear the PLM.",
                QMessageBox.StandardButton.Ok,
            )
            return
        if hasattr(self.current_data_source, "send_command"):
            self.current_data_source.send_command("clear_plm")
            QMessageBox.information(
                self.view,
                "Clear PLM",
                "Please reboot the board",
                QMessageBox.StandardButton.Ok,
            )
        else:
            QMessageBox.information(
                self.view,
                "Not Supported",
                "Clear PLM only works with serial connections",
                QMessageBox.StandardButton.Ok,
            )

    def get_current_data_source_type(self):
        sidebar = self.view.get_sidebar()
        return sidebar.get_data_source_combo().currentText().lower()

    def get_selected_port(self):
        sidebar = self.view.get_sidebar()
        port_text = sidebar.get_port_dropdown().currentText()
        return port_text.split(" (")[0] if " (" in port_text else port_text

    def refresh_ports(self):
        from cure_ground.data_sources import SerialDataSource

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
                if widget and hasattr(widget, "text") and widget.text() == "COM Port:":
                    widget.hide()
        else:
            sidebar.get_port_dropdown().show()
            for i in range(sidebar.layout().count()):
                widget = sidebar.layout().itemAt(i).widget()
                if widget and hasattr(widget, "text") and widget.text() == "COM Port:":
                    widget.show()
            self.refresh_ports()

        if self.connected:
            self.disconnect_and_hide()
        sidebar.update_connect_button_text("Connect")

    def clear_graphs(self):
        # Clear merged graph lines (new graph implementation)
        if self.merged_graph:
            self.merged_graph.clear_graph()

        # Also clear the model's stored data
        self.model.clear_graph_data()

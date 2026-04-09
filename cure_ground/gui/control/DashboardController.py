import time
import math
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox
import os
from typing import Any, Optional

from cure_ground.data_sources.DataSourceFactory import DataSourceFactory
from cure_ground.gui.model.StatusModel import StatusModel
from cure_ground.gui.view import MainWindow
from cure_ground.gui.view.OrientationVisual import OrientationView
from cure_ground.gui.view.Graphs import MergedGraph
from cure_ground.gui.view.TextFormatter import TextFormatter
from cure_ground.gui.view.CommandTerminalDialog import CommandTerminalDialog


class DashboardController:
    def __init__(self, view):
        self.view: MainWindow = view
        self.model = StatusModel()
        self.text_formatter = TextFormatter()
        self.streaming = False
        self.timer = QTimer()
        self.current_data_source = None
        self.connected = False
        self.graph_visible = False
        self._last_text_update = 0

        # Graphs
        self.merged_graph = None
        self.orientation_visual = None

        self.csv_recordings_dir = "recordings"
        self.csv_file_path: Optional[str] = None

        self.setup_connections()
        self.refresh_ports()

    # --------------------- SETUP ---------------------
    def setup_connections(self):
        sidebar = self.view.get_sidebar()
        sidebar.get_data_source_combo().currentTextChanged.connect(
            self.on_data_source_changed
        )
        sidebar.get_refresh_button().clicked.connect(self.refresh_sidebar_selector)
        sidebar.get_connect_button().clicked.connect(self.toggle_connection_status)
        sidebar.get_live_update_button().clicked.connect(self.toggle_streaming)
        sidebar.get_graph_button().clicked.connect(self.toggle_graph)
        sidebar.get_clear_plm_button().clicked.connect(self.clear_plm)
        sidebar.get_command_mode_button().clicked.connect(self.open_command_mode)
        sidebar.get_port_dropdown().currentIndexChanged.connect(
            self.on_csv_file_selected
        )
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
            if self.get_current_data_source_type() == "radio":
                sidebar.get_command_mode_button().show()
            else:
                sidebar.get_command_mode_button().hide()
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
                self.csv_file_path = self.get_selected_csv_file()
                if not self.csv_file_path:
                    QMessageBox.warning(
                        self.view,
                        "Connection Error",
                        f"No CSV files found in {self.csv_recordings_dir}",
                    )
                    return False

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
            if source_type == "csv":
                self.model.clear_local_save_path()
            else:
                # use current time mm-dd-yy_hh-mm-ss format
                os.makedirs(self.csv_recordings_dir, exist_ok=True)
                self.model.set_local_save_path(
                    os.path.join(
                        self.csv_recordings_dir,
                        f"data_{time.strftime('%m-%d-%y_%H-%M-%S')}.csv",
                    )
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
    @staticmethod
    def _format_display_value(value):
        if value in (None, "", "N/A"):
            return "N/A"

        numeric_value = None
        if isinstance(value, (int, float)):
            numeric_value = float(value)
        elif isinstance(value, str):
            stripped = value.strip()
            if not stripped or stripped.startswith("["):
                return value
            try:
                numeric_value = float(stripped)
            except ValueError:
                return value
        else:
            return value

        if not math.isfinite(numeric_value):
            return "N/A"

        if abs(numeric_value - round(numeric_value)) < 1e-9:
            return str(int(round(numeric_value)))

        return f"{numeric_value:.2f}"

    def update_status(self):
        if not self.connected or not self.current_data_source:
            return

        if self.model.update_from_data_source():
            status_data = self.model.get_all_data()

            now = time.time()
            if now - self._last_text_update > 0.05:  # update text at ~20 FPS max
                # Round numeric telemetry values (including numeric strings) for display.
                display_status_data = {
                    key: self._format_display_value(value)
                    for key, value in status_data.items()
                }
                left_text = self.text_formatter.get_left_column_text(
                    display_status_data
                )
                right_text = self.text_formatter.get_right_column_text(
                    display_status_data
                )
                self.view.get_status_display().update_text(left_text, right_text)
                self._last_text_update = now

        # === Update packet retention bar ===
        retention_getter = getattr(
            self.current_data_source, "get_packet_retention_ratio", None
        )
        if callable(retention_getter):
            try:
                raw_retention: Any = retention_getter()
                retention_ratio = float(raw_retention)
            except (TypeError, ValueError):
                retention_ratio = 1.0
        else:
            retention_ratio = 1.0  # Default to 100% if not supported

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

    def get_selected_csv_file(self) -> Optional[str]:
        dropdown = self.view.get_sidebar().get_port_dropdown()
        selected_path = dropdown.currentData()
        if isinstance(selected_path, str) and os.path.isfile(selected_path):
            return selected_path

        selected_name = dropdown.currentText().strip()
        if not selected_name or selected_name == "No CSV files found":
            return None

        fallback_path = os.path.join(self.csv_recordings_dir, selected_name)
        return fallback_path if os.path.isfile(fallback_path) else None

    def _get_file_sort_timestamp(self, file_path: str) -> float:
        file_stats = os.stat(file_path)
        # st_birthtime is used when available; fall back to mtime on systems that
        # do not expose file creation time.
        return getattr(file_stats, "st_birthtime", file_stats.st_mtime)

    def refresh_sidebar_selector(self):
        if self.get_current_data_source_type() == "csv":
            self.refresh_csv_files()
        else:
            self.refresh_ports()

    def refresh_ports(self):
        from cure_ground.data_sources import SerialDataSource

        temp_source = SerialDataSource()
        all_ports = temp_source.get_available_ports()

        available_ports = [p for p in all_ports if p != "No Ports Available"]
        radio_ports = DataSourceFactory.detect_radio_ports()

        dropdown = self.view.get_sidebar().get_port_dropdown()
        dropdown.clear()
        add_at_the_end = []
        if not available_ports:
            dropdown.addItem("No ports available")
        else:
            for port in available_ports:
                if port in radio_ports:
                    dropdown.addItem(f"{port} (Radio)")
                else:
                    add_at_the_end.append(port)
            for port in add_at_the_end:
                dropdown.addItem(port)

    def refresh_csv_files(self):
        os.makedirs(self.csv_recordings_dir, exist_ok=True)
        csv_files = []
        for filename in os.listdir(self.csv_recordings_dir):
            if not filename.lower().endswith(".csv"):
                continue
            file_path = os.path.join(self.csv_recordings_dir, filename)
            if os.path.isfile(file_path):
                csv_files.append(
                    (self._get_file_sort_timestamp(file_path), filename, file_path)
                )

        csv_files.sort(key=lambda row: (row[0], row[1].lower()), reverse=True)
        dropdown = self.view.get_sidebar().get_port_dropdown()
        dropdown.clear()

        if not csv_files:
            self.csv_file_path = None
            dropdown.addItem("No CSV files found")
            return

        for _, filename, file_path in csv_files:
            dropdown.addItem(filename, userData=file_path)
        self.csv_file_path = self.get_selected_csv_file()

    def on_csv_file_selected(self, _index: int):
        if self.get_current_data_source_type() != "csv":
            return
        self.csv_file_path = self.get_selected_csv_file()

    def on_data_source_changed(self, source_name):
        source_name = source_name.lower()
        sidebar = self.view.get_sidebar()

        if source_name == "csv":
            self.refresh_csv_files()
        elif source_name in {"radio", "serial"}:
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

    def _send_raw_command(self, command: str) -> bool:
        if self.current_data_source is None:
            return False

        send_command = getattr(self.current_data_source, "send_command", None)
        if callable(send_command):
            try:
                return bool(send_command(command, add_newline=True))
            except TypeError:
                try:
                    return bool(send_command(command))
                except Exception:
                    pass
            except Exception:
                pass

        serial_obj = getattr(self.current_data_source, "ser", None)
        if serial_obj is None or not getattr(serial_obj, "is_open", False):
            return False

        try:
            serial_obj.write((command + "\n").encode("utf-8"))
            serial_obj.flush()
            return True
        except Exception:
            return False

    def open_command_mode(self):
        if not self.connected or self.current_data_source is None:
            QMessageBox.information(
                self.view, "Not Connected", "Please connect to a data source first."
            )
            return

        serial_obj = getattr(self.current_data_source, "ser", None)
        if serial_obj is None or not getattr(serial_obj, "is_open", False):
            QMessageBox.information(
                self.view,
                "Unsupported Source",
                "Command mode requires an active serial/radio connection.",
            )
            return

        was_streaming = self.streaming
        if was_streaming:
            self.toggle_streaming()

        if not self._send_raw_command("ccc"):
            QMessageBox.warning(
                self.view,
                "Command Mode Error",
                "Failed to send 'ccc' to enter command mode.",
            )
            if was_streaming and not self.streaming:
                self.toggle_streaming()
            return

        terminal_dialog = CommandTerminalDialog(self.current_data_source, self.view)
        terminal_dialog.append_output("> ccc")

        help_timer = QTimer(terminal_dialog)
        help_timer.setSingleShot(True)

        def send_initial_help():
            if not terminal_dialog.isVisible():
                return
            if not self._send_raw_command("help"):
                terminal_dialog.append_output("[Warn] Failed to send startup 'help'")
                return
            terminal_dialog.append_output("> help")

        help_timer.timeout.connect(send_initial_help)
        help_timer.start(300)

        terminal_dialog.exec()

        if was_streaming and not self.streaming and self.connected:
            self.toggle_streaming()

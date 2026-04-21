from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
)


class CommandTerminalDialog(QDialog):
    def __init__(self, data_source, parent=None):
        super().__init__(parent)
        self.data_source = data_source
        self._exit_sent = False
        self.setWindowTitle("Avionics Shell")
        self.resize(800, 500)

        self.output_box = QPlainTextEdit(self)
        self.output_box.setReadOnly(True)

        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("Enter shell command and press Enter...")

        self.send_button = QPushButton("Send", self)
        self.close_button = QPushButton("Close", self)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_line)
        input_row.addWidget(self.send_button)

        root = QVBoxLayout(self)
        root.addWidget(self.output_box)
        root.addLayout(input_row)
        root.addWidget(self.close_button)

        self.send_button.clicked.connect(self.send_current_command)
        self.input_line.returnPressed.connect(self.send_current_command)
        self.close_button.clicked.connect(self.close)

        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(100)
        self.poll_timer.timeout.connect(self.poll_serial_output)
        self.poll_timer.start()

    def append_output(self, text: str):
        if not text:
            return
        self.output_box.appendPlainText(text)

    def send_current_command(self):
        command = self.input_line.text().strip()
        if not command:
            return

        if not self._send_line(command):
            QMessageBox.warning(
                self,
                "Command Failed",
                "Failed to send command. Check connection status.",
            )
            return

        self.append_output(f"> {command}")
        self.input_line.clear()

    def poll_serial_output(self):
        serial_obj = getattr(self.data_source, "ser", None)
        if serial_obj is None or not getattr(serial_obj, "is_open", False):
            return

        waiting = getattr(serial_obj, "in_waiting", 0)
        if waiting <= 0:
            return

        try:
            data = serial_obj.read(waiting)
            if not data:
                return
            text = data.decode("utf-8", errors="replace")
            if text:
                self.append_output(text.rstrip("\n"))
        except Exception as exc:
            self.append_output(f"[Read error] {exc}")

    def _send_line(self, command: str) -> bool:
        if hasattr(self.data_source, "send_command"):
            try:
                return bool(self.data_source.send_command(command, add_newline=True))
            except TypeError:
                try:
                    return bool(self.data_source.send_command(command))
                except Exception:
                    pass
            except Exception:
                pass

        serial_obj = getattr(self.data_source, "ser", None)
        if serial_obj is None or not getattr(serial_obj, "is_open", False):
            return False

        try:
            serial_obj.write((command + "\n").encode("utf-8"))
            serial_obj.flush()
            return True
        except Exception:
            return False

    def _send_exit_once(self):
        if self._exit_sent:
            return

        if self._send_line("exit"):
            self._exit_sent = True

    def closeEvent(self, event):
        if self.poll_timer.isActive():
            self.poll_timer.stop()

        self._send_exit_once()
        super().closeEvent(event)

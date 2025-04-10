import sys
import serial.tools.list_ports  # To list available COM ports
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout,
    QWidget, QComboBox, QMessageBox 
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QTimer

from get_status import get_status, clear_post_launch_mode


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Dashboard")

        # Get the DPI scale factor and adjust window size
        screen = QApplication.primaryScreen()
        scale_factor = screen.devicePixelRatio()

        # Scale the window size to counteract DPI scaling
        self.setFixedSize(int(1920 / scale_factor), int(1080 / scale_factor))

        self.set_background_image("dashboardImages/dashboardBG.png")
        self.add_overlay_image("dashboardImages/BlackScreen.png")

        self.font_family = self.load_custom_font("NbpInformaFivesix-2dXW.ttf")

        # Create text display area (initially hidden)
        self.left_column = self.add_custom_text("", self.font_family, 25, "#C5FFBF", 375, 51)
        self.right_column = self.add_custom_text("", self.font_family, 25, "#C5FFBF", 950, 51)

        self.left_column.hide()
        self.right_column.hide()

        self.create_sidebar()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_text)  # Calls show_text() every second
        self.streaming = False  # Flag to track streaming state

    def set_background_image(self, image_path):
        palette = self.palette()
        pixmap = QPixmap(image_path)

        pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)

        brush = QBrush(pixmap)
        palette.setBrush(QPalette.ColorRole.Window, brush)

        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def add_overlay_image(self, image_path):
        self.overlay_label = QLabel(self)
        overlay_pixmap = QPixmap(image_path)

        overlay_pixmap = overlay_pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)

        self.overlay_label.setPixmap(overlay_pixmap)
        self.overlay_label.setGeometry(0, 0, self.width(), self.height())

    def load_custom_font(self, font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            return font_family
        else:
            print(f"Error: Could not load font from {font_path}")
            return "Arial"

    def add_custom_text(self, text, font_family, font_size, color, x, y):
        text_label = QLabel(self)
        text_label.setText(text)

        font = QFont(font_family, font_size)
        text_label.setFont(font)

        text_label.setStyleSheet(f"color: {color}; background-color: transparent; padding: 10px;")
        text_label.setWordWrap(True)
        text_label.move(x, y)

        text_label.raise_()

        return text_label

    def create_sidebar(self):
        sidebar = QWidget(self)
        sidebar.setGeometry(75, 80, 250, 700)
        sidebar.setStyleSheet("background-color: rgba(10, 10, 10, 150); border-radius: 10px;")

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 20)

        # Dropdown for selecting ports
        self.port_dropdown = QComboBox()
        self.refresh_ports()

        self.port_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #2a3a4a;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QComboBox:hover {
                background-color: #3a4a5a;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #4a5a6a;
            }
        """)

        layout.addWidget(self.port_dropdown)

        # Refresh button
        refresh_button = QPushButton("Refresh Ports")
        refresh_button.setFont(QFont(self.font_family, 20))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2a3a4a;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a4a5a;
            }
            QPushButton:pressed {
                background-color: #4a5a6a;
            }
        """)

        refresh_button.clicked.connect(self.refresh_ports)
        layout.addWidget(refresh_button)

        # Status button
        status_button = QPushButton("Status")
        status_button.setFont(QFont(self.font_family, 20))
        status_button.setStyleSheet(refresh_button.styleSheet())  

        status_button.clicked.connect(self.show_text)  # Show status info
        status_button.clicked.connect(self.show_buttons)  # Show floating button
        layout.addWidget(status_button)

        layout.addStretch()  
        sidebar.raise_()

        # Create live updating button (initially hidden)
        self.update_button = QPushButton("Live Update", self)
        self.update_button.setFont(QFont(self.font_family, 20))
        self.update_button.setGeometry (1260, 750, 200, 50)  # Position it
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #2a3a4a;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a4a5a;
            }
            QPushButton:pressed {
                background-color: #4a5a6a;
            }
        """)
        self.update_button.hide()  # Hide it initially
        self.update_button.clicked.connect(self.toggle_streaming)

        # Create button to clear plm (hidden initially)
        self.clear = QPushButton("Clear PLM", self)
        self.clear.setFont(QFont(self.font_family, 20))
        self.clear.setGeometry (1260, 690, 200, 50)  # Position it
        self.clear.setStyleSheet("""
            QPushButton {
                background-color: #2a3a4a;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a4a5a;
            }
            QPushButton:pressed {
                background-color: #4a5a6a;
            }
        """)
        self.clear.hide()  # Hide it initially
        self.clear.clicked.connect(self.clear_plm)

    def show_buttons(self):
        self.update_button.show()
        self.streaming = False  # Reset streaming state

        self.clear.show()

    def refresh_ports(self):
        self.port_dropdown.clear()
        ports = serial.tools.list_ports.comports()
        port_names = [port.device for port in ports]
        if port_names:
            self.port_dropdown.addItems(port_names)
        else:
            self.port_dropdown.addItem("No Ports Available")

    def toggle_streaming(self):
        if self.streaming:
            self.timer.stop()
            self.update_button.setText("Start Updating")
        else:
            self.timer.start(1000)  # 1000 ms = 1 second
            self.update_button.setText("Stop Updating")
    
        self.streaming = not self.streaming  # Toggle the state
        0

    def clear_plm(self):
        selected_port = self.port_dropdown.currentText()
        if selected_port != "No Ports Available":
            clear_post_launch_mode(selected_port)
            QMessageBox.information(self, "", "Please reboot the board", QMessageBox.StandardButton.Ok)

    def show_text(self):
        selected_port = self.port_dropdown.currentText()
        if selected_port == "No Ports Available":
            return  # Do nothing if no ports are available

        status_data = get_status(selected_port)

        left_text = (self.get_launch_predictor_text(status_data) + "\n\n" +
                    self.get_apogee_detector_text(status_data) + "\n\n" +
                    self.get_data_saver_text(status_data) + "\n\n" +
                    self.get_flash_text(status_data))

        right_text = self.get_sensors_text(status_data)

        self.left_column.setText(left_text)
        self.right_column.setText(right_text)

        self.left_column.adjustSize()
        self.right_column.adjustSize()
        self.left_column.show()
        self.right_column.show()


    def get_launch_predictor_text(self, status_data):
        return f"""--Launch Predictor--
Launched: {status_data.get('launchPredictorLaunched', 'N/A')}
Launched Time: {status_data.get('launchPredictorLaunchedTime', 'N/A')}
Median Acceleration Squared: {status_data.get('launchPredictorMedianAccelerationSquared', 'N/A')}"""

    def get_apogee_detector_text(self, status_data):
        return f"""--Apogee Detector--
Apogee Detected: {status_data.get('apogeeDetected', 'N/A')}
Estimated Altitude: {status_data.get('estimatedAltitude', 'N/A')}
Estimated Velocity: {status_data.get('estimatedVelocity', 'N/A')}
Inertial Vertical Acceleration: {status_data.get('inertialVerticalAcceleration', 'N/A')}
Vertical Axis: {status_data.get('verticalAxis', 'N/A')}
Vertical Direction: {status_data.get('verticalDirection', 'N/A')}
Apogee Altitude: {status_data.get('apogeeAltitude', 'N/A')}"""

    def get_data_saver_text(self, status_data):
        return f"""--Data Saver--
Post Launch Mode: {status_data.get('postLaunchMode', 'N/A')}
Rebooted in Post Launch Mode (won't save): {status_data.get('rebootedInPostLaunchMode', 'N/A')}
Last Timestamp: {status_data.get('lastTimestamp', 'N/A')}
Last Data Point Value: {status_data.get('lastDataPointValue', 'N/A')}
Super Loop Average Hz: {status_data.get('superLoopAverageHz', 'N/A')}"""

    def get_flash_text(self, status_data):
        return f"""--Flash--
Stopped writing b/c wrapped around to launch address: {status_data.get('chipFullDueToPostLaunchProtection', 'N/A')}
Launch Write Address: {status_data.get('launchWriteAddress', 'N/A')}
Next Write Address: {status_data.get('nextWriteAddress', 'N/A')}
Buffer Index: {status_data.get('bufferIndex', 'N/A')}
Buffer Flushes: {status_data.get('bufferFlushes', 'N/A')}"""

    def get_sensors_text(self, status_data):
        return f"""--Sensors--
Accelerometer X: {status_data.get('aclx', 'N/A')}
Accelerometer Y: {status_data.get('acly', 'N/A')}
Accelerometer Z: {status_data.get('aclz', 'N/A')}
Gyroscope X: {status_data.get('gyrox', 'N/A')}
Gyroscope Y: {status_data.get('gyroy', 'N/A')}
Gyroscope Z: {status_data.get('gyroz', 'N/A')}
Magnetometer X: {status_data.get('magx', 'N/A')}
Magnetometer Y: {status_data.get('magy', 'N/A')}
Magnetometer Z: {status_data.get('magz', 'N/A')}
Temperature: {status_data.get('temp', 'N/A')}
Pressure: {status_data.get('pressure', 'N/A')}
Altitude: {status_data.get('alt', 'N/A')}"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

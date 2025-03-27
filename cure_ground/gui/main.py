import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFont, QFontDatabase
from PyQt6.QtCore import Qt

from get_status import get_status


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Dashboard")
       
        # Get the DPI scale factor and adjust window size
        screen = QApplication.primaryScreen()
        scale_factor = screen.devicePixelRatio()
       
        # Scale the window size to counteract DPI scaling
        self.setFixedSize(int(1920 / scale_factor), int(1080 / scale_factor))
        
        # Set background image
        self.set_background_image("dashboardImages/dashboardBG.png")
       
        # Add overlay image
        self.add_overlay_image("dashboardImages/BlackScreen.png")
        
        self.font_family = self.load_custom_font("NbpInformaFivesix-2dXW.ttf")  # Replace with your TTF file path
        
        # Create text display area (initially hidden)
        self.left_column = self.add_custom_text("", self.font_family, 25, "#C5FFBF", 375, 51)
        self.right_column = self.add_custom_text("", self.font_family, 25, "#C5FFBF", 950, 51)
        
        self.left_column.hide()
        self.right_column.hide()
        
        # Create sidebar with buttons
        self.create_sidebar()
        
    def set_background_image(self, image_path):
        palette = self.palette()
        pixmap = QPixmap(image_path)
       
        # Scale background image to window size
        pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
       
        brush = QBrush(pixmap)
        palette.setBrush(QPalette.ColorRole.Window, brush)
       
        self.setPalette(palette)
        self.setAutoFillBackground(True)
   
    def add_overlay_image(self, image_path):
        self.overlay_label = QLabel(self)
        overlay_pixmap = QPixmap(image_path)
       
        # Scale the overlay to match the adjusted window size
        overlay_pixmap = overlay_pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
       
        self.overlay_label.setPixmap(overlay_pixmap)
       
        # Cover the window with the overlay
        self.overlay_label.setGeometry(0, 0, self.width(), self.height())
    
    def load_custom_font(self, font_path):
        """Load a custom TTF font file and return its font family name"""
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            return font_family
        else:
            print(f"Error: Could not load font from {font_path}")
            return "Arial"
    
    def add_custom_text(self, text, font_family, font_size, color, x, y):
        # Create a label for the text
        text_label = QLabel(self)
        text_label.setText(text)
        
        font = QFont(font_family, font_size)
        text_label.setFont(font)
        
        text_label.setStyleSheet(f"color: {color}; background-color: transparent; padding: 10px;")
        
        text_label.setWordWrap(True)
        
        text_label.move(x, y)
        
        # Ensure text is visible above all other elements
        text_label.raise_()
        
        return text_label
    
    def create_sidebar(self):
        # Create a widget to hold the sidebar buttons
        sidebar = QWidget(self)
        sidebar.setGeometry(75, 80, 250, 700)
        sidebar.setStyleSheet("background-color: rgba(10, 10, 10, 150); border-radius: 10px;")

        # Create layout for buttons
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 20)

        # Create button to fetch and display status
        button = QPushButton("Status")
        
        font = QFont(self.font_family, 20)
        button.setFont(font)

        button.setStyleSheet("""
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

        # Correctly connect button to show_text()
        button.clicked.connect(self.show_text)

        layout.addWidget(button)

        # Add a stretch at the end to push all buttons to the top
        layout.addStretch()

        # Ensure sidebar is visible above overlay
        sidebar.raise_()


    
    def show_text(self):
        status_data = get_status("COM4")
        
        left_text = (self.get_launch_predictor_text(status_data) + "\n\n" +
                    self.get_apogee_detector_text(status_data) + "\n\n" +
                    self.get_data_saver_text(status_data) + "\n\n" +
                    self.get_flash_text(status_data))
        
        right_text = self.get_sensors_text(status_data)
        
        self.left_column.setText(left_text)
        self.right_column.setText(right_text)
        
        # Adjust size and show both columns
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
Temperature: {status_data.get('temp', 'N/A')}
Pressure: {status_data.get('pressure', 'N/A')}
Altitude: {status_data.get('alt', 'N/A')}
Magnetometer X: {status_data.get('magx', 'N/A')}
Magnetometer Y: {status_data.get('magy', 'N/A')}
Magnetometer Z: {status_data.get('magz', 'N/A')}"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
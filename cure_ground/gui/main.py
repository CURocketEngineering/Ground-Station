import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFont, QFontDatabase
from PyQt6.QtCore import Qt

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
        
        # Load custom font
        self.font_family = self.load_custom_font("NbpInformaFivesix-2dXW.ttf")  # Replace with your TTF file path
        
        # Create text display area (initially hidden)
        self.left_column = self.add_custom_text("", self.font_family, 20, "#C5FFBF", 375, 51)
        self.right_column = self.add_custom_text("", self.font_family, 20, "#C5FFBF", 950, 51)
        
        # Initially hide both columns
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
            # Get the font family name from the loaded font
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            return font_family
        else:
            print(f"Error: Could not load font from {font_path}")
            return "Arial"  # Fallback to a system font if loading fails
    
    def add_custom_text(self, text, font_family, font_size, color, x, y):
        # Create a label for the text
        text_label = QLabel(self)
        text_label.setText(text)
        
        # Set font properties
        font = QFont(font_family, font_size)
        text_label.setFont(font)
        
        # Set text color and background
        text_label.setStyleSheet(f"color: {color}; background-color: transparent; padding: 10px;")
        
        # Enable text wrapping
        text_label.setWordWrap(True)
        
        # Position the text
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
        
        # Define button sections from the data
        sections = {
            "Status": self.get_all_text()
        }
        
        # Create buttons for each section
        for section_name, section_text in sections.items():
            button = QPushButton(section_name)

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
            
            # Connect the button click to show the corresponding text
            # We need to use a lambda with a default argument to capture the current value
            button.clicked.connect(lambda checked=False, text=section_text: self.show_text(text))
            
            layout.addWidget(button)  # Changed from addButton to addWidget
        
        # Add a stretch at the end to push all buttons to the top
        layout.addStretch()
        
        # Ensure sidebar is visible above overlay
        sidebar.raise_()
    
    def show_text(self, text):
        # Separate sections
        launch_predictor = self.get_launch_predictor_text()
        apogee_detector = self.get_apogee_detector_text()
        data_saver = self.get_data_saver_text()
        flash = self.get_flash_text()
        sensors = self.get_sensors_text()
        
        # First column contains all sections except sensors
        left_text = (launch_predictor + "\n\n" + 
                    apogee_detector + "\n\n" + 
                    data_saver + "\n\n" + 
                    flash)
        
        # Second column contains only sensors data
        right_text = sensors
        
        # Set text in two columns
        self.left_column.setText(left_text)
        self.right_column.setText(right_text)
        
        # Adjust size and show both columns
        self.left_column.adjustSize()
        self.right_column.adjustSize()
        self.left_column.show()
        self.right_column.show()
    
    # Methods to format the different text sections
    def get_launch_predictor_text(self):
        return """--Launch Predictor--
Launched: [value]
Launched Time: [value]
Median Acceleration Squared: [value]"""
    
    def get_apogee_detector_text(self):
        return """--Apogee Detector--
Apogee Detected: [value]
Estimated Altitude: [value]
Estimated Velocity: [value]
Inertial Vertical Acceleration: [value]
Vertical Axis: [value]
Vertical Direction: [value]
Apogee Altitude: [value]"""
    
    def get_data_saver_text(self):
        return """--Data Saver--
Post Launch Mode: [value]
Rebooted in Post Launch Mode (won't save): [value]
Last Timestamp: [value]
Last Data Point Value: [value]
Super loop average hz: [value]"""
    
    def get_flash_text(self):
        return """--Flash--
Stopped writing b/c wrapped around to launch address: [value]
Launch Write Address: [value]
Next Write Address: [value]
Buffer Index: [value]
Buffer Flushes: [value]"""
    
    def get_sensors_text(self):
        return """--Sensors--
Accelerometer X: [value]
Accelerometer Y: [value]
Accelerometer Z: [value]
Gyroscope X: [value]
Gyroscope Y: [value]
Gyroscope Z: [value]
Temperature: [value]
Pressure: [value]
Altitude: [value]
Magnetometer X: [value]
Magnetometer Y: [value]
Magnetometer Z: [value]"""
    
    def get_all_text(self):
        # Combine all sections
        return (self.get_launch_predictor_text() + "\n\n" + 
                self.get_apogee_detector_text() + "\n\n" + 
                self.get_data_saver_text() + "\n\n" + 
                self.get_flash_text() + "\n\n" + 
                self.get_sensors_text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
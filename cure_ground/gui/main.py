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
        self.text_display = self.add_custom_text("", self.font_family, 18, "#C5FFBF", 375, 51)
        self.text_display.hide()
        
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
        text_label.setStyleSheet(f"color: {color}; background-color: rgba(0, 0, 0, 100); padding: 10px;")
        
        # Enable text wrapping
        text_label.setWordWrap(True)
        
        # Set a fixed width but allow height to adjust
        text_label.setFixedWidth(800)
        
        # Position the text
        text_label.move(x, y)
        
        # Ensure text is visible above all other elements
        text_label.raise_()
        
        return text_label
    
    def create_sidebar(self):
        # Create a widget to hold the sidebar buttons
        sidebar = QWidget(self)
        sidebar.setGeometry(20, 100, 180, 600)
        sidebar.setStyleSheet("background-color: rgba(10, 10, 10, 150); border-radius: 10px;")
        
        # Create layout for buttons
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 20)
        
        # Define button sections from the data
        sections = {
            "Status": self.get_status_text()
        }
        
        # Create buttons for each section
        for section_name, section_text in sections.items():
            button = QPushButton(section_name)

            font = QFont(self.font_family, 15)
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
        # Update text display and show it
        self.text_display.setText(text)
        self.text_display.adjustSize()
        self.text_display.show()
    
    # Methods to format the different text sections
    def get_status_text(self):
        return """--Launch Predictor--
Launched: [value]
Launched Time: [value]
Median Acceleration Squared: [value]

--Apogee Detector--
Apogee Detected: [value]
Estimated Altitude: [value]
Estimated Velocity: [value]
Inertial Vertical Acceleration: [value]
Vertical Axis: [value]
Vertical Direction: [value]
Apogee Altitude: [value]

--Data Saver--
Post Launch Mode: [value]
Rebooted in Post Launch Mode (won't save): [value]
Last Timestamp: [value]
Last Data Point Value: [value]
Super loop average hz: [value]

--Flash--
Stopped writing b/c wrapped around to launch address: [value]
Launch Write Address: [value]
Next Write Address: [value]
Buffer Index: [value]
Buffer Flushes: [value]

--Sensors--
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
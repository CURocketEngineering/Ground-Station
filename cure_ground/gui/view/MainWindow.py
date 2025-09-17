from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt6.QtGui import QFontDatabase, QPalette, QBrush, QPixmap
from PyQt6.QtCore import Qt

from view.Sidebar import Sidebar
from view.StatusDisplay import StatusDisplay

class MainWindow(QMainWindow):
    # Defining image paths

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Dashboard")
        
        # Get the DPI scale factor and adjust window size
        screen = QApplication.primaryScreen()
        scale_factor = screen.devicePixelRatio()
        self.setFixedSize(int(1920 / scale_factor), int(1080 / scale_factor))

        # Load and set background image
        self.set_background_image("resources/DashboardImage.png")
        
        # Load custom font
        self.font_family = self.load_custom_font("resources/NbpInformaFivesix-2dXW.ttf")
        
        # Create UI components
        self.sidebar = Sidebar(self, self.font_family)
        self.status_display = StatusDisplay(self, self.font_family)
        
    def load_custom_font(self, font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            return QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            print(f"Error: Could not load font from {font_path}")
            return "Arial"
            
    def set_background_image(self, image_path):
        try:
            palette = self.palette()
            pixmap = QPixmap(image_path)
            
            # Scale the image to fit the window
            pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
            
            brush = QBrush(pixmap)
            palette.setBrush(QPalette.ColorRole.Window, brush)
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        except Exception as e:
            print(f"Error setting background image: {e}")
        
    def get_sidebar(self):
        return self.sidebar
        
    def get_status_display(self):
        return self.status_display
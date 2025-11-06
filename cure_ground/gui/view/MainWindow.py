from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt6.QtGui import QFontDatabase, QPalette, QBrush, QPixmap
from PyQt6.QtCore import Qt

from cure_ground.gui.view.Sidebar import Sidebar
from cure_ground.gui.view.StatusDisplay import StatusDisplay

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Dashboard")
        
        # Get the DPI scale factor and adjust window size
        screen = QApplication.primaryScreen()
        scale_factor = screen.devicePixelRatio()
        self.setFixedSize(int(1920 / scale_factor), int(1080 / scale_factor))

        # Load and set background image
        self.set_background_image("cure_ground/gui/resources/Dashboard.png")
        
        # Load custom font
        self.font_family = self.load_custom_font("cure_ground/gui/resources/NbpInformaFivesix-2dXW.ttf")
        
        # Create UI components
        self.sidebar = Sidebar(self, self.font_family)
        self.status_display = StatusDisplay(self, self.font_family)
        
        # Graph placeholders
        self.altitude_graph = None
        self.accel_graph = None
        self.orientation_visual = None

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
        
    def set_altitude_graph(self, graph_widget):
        self.altitude_graph = graph_widget
        if self.altitude_graph:
            self.altitude_graph.setParent(self)
            self.altitude_graph.move(975, 460)
            self.altitude_graph.resize(500, 350)
            self.altitude_graph.raise_()
            self.altitude_graph.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop, True)

    def set_accelerometer_graph(self, graph_widget):
        self.accel_graph = graph_widget
        if self.accel_graph:
            self.accel_graph.setParent(self)
            self.accel_graph.move(975, 80)
            self.accel_graph.resize(500, 350)
            self.accel_graph.raise_()
            self.accel_graph.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop, True)

    def set_orientation_visual(self, visual_widget):
        self.orientation_visual = visual_widget
        if self.orientation_visual:
            self.orientation_visual.setParent(self)
            self.orientation_visual.move(300, 80)
            self.orientation_visual.resize(500, 350)
            self.orientation_visual.raise_()
            self.orientation_visual.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop, True)
            
    def toggle_graph_visual_visibility(self, visible):
        if self.altitude_graph:
            self.altitude_graph.setVisible(visible)
        if self.accel_graph:
            self.accel_graph.setVisible(visible)
        if self.orientation_visual:
            self.orientation_visual.setVisible(visible)
        if visible:
            if self.altitude_graph: self.altitude_graph.raise_()
            if self.accel_graph: self.accel_graph.raise_()
            if self.orientation_visual: self.orientation_visual.raise_()
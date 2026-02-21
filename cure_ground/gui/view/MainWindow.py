from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QFontDatabase, QPalette, QBrush, QPixmap
from PyQt6.QtCore import Qt

from cure_ground.gui.view.Sidebar import Sidebar
from cure_ground.gui.view.StatusDisplay import StatusDisplay
<<<<<<< HEAD
from cure_ground.gui.view.OrientationVisual import OrientationView
from cure_ground.gui.view.PacketLossIndicator import PacketLossIndicator
=======

>>>>>>> f8ca19ee8b67f6671a8fd86bd96d274c3965168a

class MainWindow(QMainWindow):
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Dashboard")
        self.resize(self.BASE_WIDTH, self.BASE_HEIGHT)

        # Load background image and custom font
        self.set_background_image("cure_ground/gui/resources/Dashboard.png")
        self.font_family = self.load_custom_font(
            "cure_ground/gui/resources/NbpInformaFivesix-2dXW.ttf"
        )

        # UI components
        self.sidebar = Sidebar(self, self.font_family)
        self.status_display = StatusDisplay(self, self.font_family)
        # After creating status_display
        self.packet_loss_indicator = PacketLossIndicator(self)
        self.packet_loss_indicator.show()  # make sure it’s visible


        # Graph placeholders (DashboardController will assign)
        self.merged_graph = None
        self.orientation_visual = None

    def load_custom_font(self, font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            return QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            print(f"Error loading font: {font_path}")
            return "Arial"

    def set_background_image(self, image_path):
        try:
            palette = self.palette()
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        except Exception as e:
            print(f"Error setting background image: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "sidebar"):
            self.sidebar.raise_()

        # Rescale background
        self.set_background_image("cure_ground/gui/resources/dashboardWhite.png")

        w = self.width() / self.BASE_WIDTH
        h = self.height() / self.BASE_HEIGHT
        scale = (w + h) / 2

        # Resize status display fonts
        font_left = self.status_display.left_column.font()
        font_left.setPointSize(int(self.status_display.base_font_size * scale))
        self.status_display.left_column.setFont(font_left)

        font_right = self.status_display.right_column.font()
        font_right.setPointSize(int(self.status_display.base_font_size * scale))
        self.status_display.right_column.setFont(font_right)

        # Reposition elements
        self.sidebar.setGeometry(int(75 * w), int(80 * h), int(300 * w), int(925 * h))
        self.status_display.left_column.move(int(365 * w), int(50 * h))
        self.status_display.right_column.move(int(675 * w), int(50 * h))

        # === Graph Layout ===
        if self.merged_graph:
            self.merged_graph.setGeometry(
                int(self.width() * 0.65),  # horizontal shift
                int(self.height() * 0.10),  # vertical shift
                int(self.width() * 0.30),  # width
                int(self.height() * 0.75),  # height
            )

        if self.orientation_visual:
            self.orientation_visual.setGeometry(
                int(self.width() * 0.30),
                int(self.height() * 0.55),
                int(self.width() * 0.30),
                int(self.height() * 0.35),
            )

<<<<<<< HEAD
        # === Packet Loss Indicator Layout ===
        if hasattr(self, "packet_loss_indicator") and self.packet_loss_indicator:
            bar_height = self.packet_loss_indicator.height()
            self.packet_loss_indicator.setGeometry(
                0,                     # x = left edge
                self.height() - bar_height,  # y = bottom edge
                self.width(),          # full width
                bar_height             # fixed height
            )
            self.packet_loss_indicator.raise_()




=======
>>>>>>> f8ca19ee8b67f6671a8fd86bd96d274c3965168a
    # Sidebar & Status access
    def get_sidebar(self):
        return self.sidebar

    def get_status_display(self):
        return self.status_display

    def set_orientation_visual(self, visual_widget):
        self.orientation_visual = visual_widget
        if visual_widget:
            visual_widget.setParent(self)
            visual_widget.show()
            visual_widget.raise_()

    def set_merged_graph(self, graph_widget):
        self.merged_graph = graph_widget
        if graph_widget:
            graph_widget.setParent(self)
            graph_widget.show()
            graph_widget.raise_()

    def toggle_graph_visual_visibility(self, visible):
        for widget in [self.merged_graph, self.orientation_visual]:
            if widget:
                widget.setVisible(visible)
                if visible:
                    widget.raise_()
<<<<<<< HEAD
    def get_packet_loss_indicator(self):
        return self.packet_loss_indicator
=======
>>>>>>> f8ca19ee8b67f6671a8fd86bd96d274c3965168a

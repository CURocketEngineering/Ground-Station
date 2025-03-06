import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor, QPainter, QBrush
from PyQt6.QtCore import Qt

class BeigeBoxBG(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            background-color: #D8D3CD;
            border: 5px solid #9B9185;
        """)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        radius = 5
        shadow_offset = 2

        # Draw screw shadows (slightly larger and offset)
        painter.setBrush(QBrush(QColor(0, 0, 0, 80)))  # Semi-transparent black for shadow
        painter.setPen(Qt.PenStyle.NoPen)

        # Top-left shadow
        painter.drawEllipse(3 + shadow_offset, 3 + shadow_offset, radius * 2, radius * 2)

        # Top-right shadow
        painter.drawEllipse((self.width() - radius * 2) - 3 + shadow_offset, 3 + shadow_offset, radius * 2, radius * 2)

        # Bottom-left shadow
        painter.drawEllipse(3 + shadow_offset, (self.height() - radius * 2) - 3 + shadow_offset, radius * 2, radius * 2)

        # Bottom-right shadow
        painter.drawEllipse((self.width() - radius * 2) - 3 + shadow_offset, (self.height() - radius * 2) - 3 + shadow_offset, radius * 2, radius * 2)

        # Draw actual screw-like circles
        painter.setBrush(QBrush(QColor(181, 181, 181)))  # Screw color
        painter.setPen(QColor(109, 109, 109))            # Screw border

        # Top-left circle
        painter.drawEllipse(3, 3, radius * 2, radius * 2)

        # Top-right circle
        painter.drawEllipse((self.width() - radius * 2) - 3, 3, radius * 2, radius * 2)

        # Bottom-left circle
        painter.drawEllipse(3, (self.height() - radius * 2) - 3, radius * 2, radius * 2)

        # Bottom-right circle
        painter.drawEllipse((self.width() - radius * 2) - 3, (self.height() - radius * 2) - 3, radius * 2, radius * 2)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI")

        self.setStyleSheet("background-color: #98C1AB;")

        self.setMinimumSize(1280, 720)

        # Create the square with screw-like circles in corners
        self.square = BeigeBoxBG(self)

        # Set shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(59, 98, 80, 255))  # Shadow color
        shadow.setOffset(0, 0)
        shadow.setBlurRadius(30)
        self.square.setGraphicsEffect(shadow)

        self.showMaximized()

    def resizeEvent(self, event):
        # Resize the square when the window resizes
        window_width = self.width()
        window_height = self.height()

        # Resize and reposition the square
        self.square.setGeometry(20, 20, window_width - 40, window_height - 40)

        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

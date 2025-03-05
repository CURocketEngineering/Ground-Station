import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI")

        self.setStyleSheet("background-color: #98C1AB;")

        self.square = QLabel(self)
        self.square.setStyleSheet("""
            background-color: #D8D3CD;
            border: 5px solid #705E5A;
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(96, 133, 116, 160))
        shadow.setOffset(10, 10)
        shadow.setBlurRadius(20)
        self.square.setGraphicsEffect(shadow)

        self.showMaximized()

    def resizeEvent(self, event):
        """ Resize the square when the window resizes """
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
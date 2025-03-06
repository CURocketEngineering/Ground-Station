import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Resizable Background Image")
        
        # Create a QLabel to hold the background image
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)

        # Load the image
        self.pixmap = QPixmap("dashboardBG.png")  # Replace with your image path

        self.setMinimumSize(1280, 720)
        self.showMaximized()

    def resizeEvent(self, event):
        # Resize the image when the window resizes
        scaled_pixmap = self.pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.bg_label.setPixmap(scaled_pixmap)
        self.bg_label.resize(self.size())

        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI")
        
        # Create a QLabel for the background image
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)

        # Load the background image
        self.bg_pixmap = QPixmap("dashboardImages/dashboardBG.png")  # Replace with your background image path

        # Create a QLabel for the first overlay image
        self.BlackScreen_label = QLabel(self)
        self.BlackScreen_label.setScaledContents(True)

        # Load the first overlay image
        self.BlackScreen_pixmap = QPixmap("dashboardImages/BlackScreen.png")  # Replace with your first overlay image path

        # Create a QLabel for the second overlay image
        self.Grid_label = QLabel(self)
        self.Grid_label.setScaledContents(True)

        # Load the second overlay image
        self.Grid_pixmap = QPixmap("dashboardImages/Grid.png")  # Replace with your second overlay image path

        # Start maximized
        self.showMaximized()

        # Set the initial images
        self.updateImages()

    def resizeEvent(self, event):
        # Resize images whenever the window resizes
        self.updateImages()
        super().resizeEvent(event)

    def updateImages(self):
        # Update the background image size
        if not self.bg_pixmap.isNull():
            scaled_bg = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg_label.setPixmap(scaled_bg)
            self.bg_label.resize(self.size())

        # Update the first overlay image size
        if not self.BlackScreen_pixmap.isNull():
            scaled_BlackScreen = self.BlackScreen_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.BlackScreen_label.setPixmap(scaled_BlackScreen)
            self.BlackScreen_label.resize(self.size())

        # Update the second overlay image size
        if not self.Grid_pixmap.isNull():
            scaled_Grid = self.Grid_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.Grid_label.setPixmap(scaled_Grid)
            self.Grid_label.resize(self.size())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
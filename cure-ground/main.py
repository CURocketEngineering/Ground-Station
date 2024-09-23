import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import cv2
import cli

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QWidget to hold everything
        widget = QWidget()
        self.setCentralWidget(widget)

        # Create a layout for the widget
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Create 5 graphs
        for _ in range(5):
            fig = Figure()
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

    def closeEvent(self, event):
        # Release the video capture when the window is closed
        self.cap.release()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    cli.main()
import sys

from PyQt6.QtWidgets import QApplication


from cure_ground.gui.view.MainWindow import MainWindow
from cure_ground.gui.control.DashboardController import DashboardController


def main():
    app = QApplication(sys.argv)

    # Create view
    view = MainWindow()

    # Create controller instance to prevent garbage collection
    _controller = DashboardController(view) 

    # Show the window
    view.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

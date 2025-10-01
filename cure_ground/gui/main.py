import sys
from PyQt6.QtWidgets import QApplication

from view.MainWindow import MainWindow
from control.DashboardController import DashboardController

def main():
    app = QApplication(sys.argv)
    
    # Create view
    view = MainWindow()
    
    # Create controller and connect it to the view
    controller = DashboardController(view)
    
    # Show the window
    view.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
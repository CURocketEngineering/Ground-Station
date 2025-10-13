import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))  # gui folder
project_root = os.path.dirname(project_root)  # cure_ground folder

# Add project root to Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
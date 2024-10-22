import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit
from PyQt6.QtCore import Qt

class CommandLineInterface(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.setWindowTitle("Command Line Interface")
        self.setGeometry(100, 100, 600, 400)

        # Create central widget and layout
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Create a text display for output
        self.output_display = QTextEdit(self)
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)

        # Create an input field for entering commands
        self.command_input = QLineEdit(self)
        layout.addWidget(self.command_input)

        # Connect the command input to a function that processes commands
        self.command_input.returnPressed.connect(self.process_command)

    def process_command(self):
        # Get the command from the input field
        command = self.command_input.text()

        # Clear the input field after capturing the command
        self.command_input.clear()

        # Process the command and show the result
        output = self.run_command(command)
        self.output_display.append(f"> {command}\n{output}")

    def run_command(self, command):
        # Simple command handling logic
        if command == "ping":
            return self.ping()
        elif command == "hello":
            return self.hello()
        elif command == "exit":
            self.close()
        else:
            return f"Unknown command: {command}"
    
    def ping(self):
        return "Pong!"

    def hello(self):
        return "Hello, world!"

    def closeEvent(self, event):
        # Handle closing the window (if needed, clean up resources here)
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = CommandLineInterface()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

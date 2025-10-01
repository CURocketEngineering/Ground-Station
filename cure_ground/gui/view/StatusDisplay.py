from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtGui import QFont

from view.Styles import BUTTON_STYLE, get_text_style

class StatusDisplay:
    def __init__(self, parent, font_family):
        self.parent = parent
        self.font_family = font_family
        self.setup_ui()
        
    def setup_ui(self):
        # Text displays
        self.left_column = self.create_text_label("", 375, 51)
        self.right_column = self.create_text_label("", 950, 51)
        
        # Control buttons
        self.update_button = self.create_button("Live Update", 1260, 750, 200, 50)
        self.clear_button = self.create_button("Clear PLM", 1260, 690, 200, 50)
        
        # Initially hide elements
        self.hide_all()
        
    def create_text_label(self, text, x, y):
        label = QLabel(self.parent)
        label.setText(text)
        label.setFont(QFont(self.font_family, 25))
        label.setStyleSheet(get_text_style())
        label.setWordWrap(True)
        label.move(x, y)
        label.raise_()  # Ensure text appears above overlay
        return label
        
    def create_button(self, text, x, y, width, height):
        button = QPushButton(text, self.parent)
        button.setFont(QFont(self.font_family, 20))
        button.setGeometry(x, y, width, height)
        button.setStyleSheet(BUTTON_STYLE)
        button.raise_()  # Ensure buttons appear above overlay
        return button
        
    def hide_all(self):
        self.left_column.hide()
        self.right_column.hide()
        self.update_button.hide()
        self.clear_button.hide()
        
    def show_text(self):
        self.left_column.show()
        self.right_column.show()
        # Ensure text stays above overlay
        self.left_column.raise_()
        self.right_column.raise_()
        
    def show_buttons(self):
        self.update_button.show()
        self.clear_button.show()
        # Ensure buttons stay above overlay
        self.update_button.raise_()
        self.clear_button.raise_()
        
    def update_text(self, left_text, right_text):
        self.left_column.setText(left_text)
        self.right_column.setText(right_text)
        self.left_column.adjustSize()
        self.right_column.adjustSize()
        # Ensure text stays above overlay after update
        self.left_column.raise_()
        self.right_column.raise_()
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QFont

from cure_ground.gui.view.Styles import get_text_style

class StatusDisplay:
    def __init__(self, parent, font_family):
        self.parent = parent
        self.font_family = font_family
        self.setup_ui()
        
    def setup_ui(self):
        # Text displays only - buttons moved to sidebar
        self.left_column = self.create_text_label("", 375, 50)
        self.right_column = self.create_text_label("", 650, 50)
        
        # Initially hide elements
        self.hide_all()
        
    def create_text_label(self, text, x, y):
        label = QLabel(self.parent)
        label.setText(text)
        label.setFont(QFont(self.font_family, 15))
        label.setStyleSheet(get_text_style())
        label.setWordWrap(True)
        label.move(x, y)
        label.raise_()
        return label
        
    def hide_all(self):
        self.left_column.hide()
        self.right_column.hide()
        
    def show_text(self):
        self.left_column.show()
        self.right_column.show()
        
    def update_text(self, left_text, right_text):
        self.left_column.setText(left_text)
        self.right_column.setText(right_text)
        self.left_column.adjustSize()
        self.right_column.adjustSize()

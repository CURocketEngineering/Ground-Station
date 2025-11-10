from PyQt6.QtWidgets import QLabel, QWidget
from PyQt6.QtGui import QFont
from cure_ground.gui.view.Styles import get_text_style

class StatusDisplay(QWidget):
    def __init__(self, parent, font_family):
        super().__init__(parent)
        self.font_family = font_family
        self.base_font_size = 15
        self.setup_ui()

    def setup_ui(self):
        self.setGeometry(100, 30, 1000, 700)

        self.left_column = self.create_text_label("", 0, 0)
        self.right_column = self.create_text_label("", 300, 0)

        self.hide_all()

    def create_text_label(self, text, x, y):
        label = QLabel(self)
        label.setText(text)
        label.setFont(QFont(self.font_family, self.base_font_size))
        label.setStyleSheet(get_text_style())
        label.setWordWrap(True)
        label.move(x, y)
        return label

    def hide_all(self):
        self.left_column.hide()
        self.right_column.hide()

    def show_text(self):
        self.show()
        self.left_column.show()
        self.right_column.show()

    def update_text(self, left_text, right_text):
        self.left_column.setText(left_text)
        self.right_column.setText(right_text)
        self.left_column.adjustSize()
        self.right_column.adjustSize()
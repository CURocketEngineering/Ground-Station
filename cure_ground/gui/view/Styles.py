# Style constants and utilities
BUTTON_STYLE = """
    QPushButton {
        background-color: #2a3a4a;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #3a4a5a;
    }
    QPushButton:pressed {
        background-color: #4a5a6a;
    }
"""

COMBO_BOX_STYLE = """
    QComboBox {
        background-color: #2a3a4a;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px;
        font-weight: bold;
    }
    QComboBox:hover {
        background-color: #3a4a5a;
    }
    QComboBox::drop-down {
        border: none;
        background-color: #4a5a6a;
    }
"""

SIDEBAR_STYLE = "background-color: rgba(10, 10, 10, 150); border-radius: 10px;"

def get_text_style(color: str = "#00FF00") -> str:
    return f"color: {color}; background-color: transparent; padding: 10px;"
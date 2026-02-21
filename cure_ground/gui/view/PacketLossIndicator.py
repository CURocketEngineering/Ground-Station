# cure_ground/gui/view/PacketLossIndicator.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QSizePolicy

class PacketLossIndicator(QWidget):
    def __init__(self, parent=None, height=25):
        super().__init__(parent)

        self.retention_ratio = 1.0
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

    def set_packet_loss(self, retention_ratio: float):
        """
        Update the retention ratio (0.0 - 1.0)
        """
        self._retention_ratio = max(0.0, min(1.0, retention_ratio))
        self.update()  # triggers repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Determine color based on retention
        color = self._retention_to_color(self._retention_ratio)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)

        # Fill rectangle for the bar
        width = int(self.width() * self._retention_ratio)
        painter.drawRect(0, 0, width, self.height())

        # Optional: Draw border for full bar
        painter.setPen(Qt.PenStyle.SolidLine)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(0, 0, self.width()-1, self.height()-1)

    def _retention_to_color(self, retention: float) -> QColor:
        """
        Maps retention ratio to color:
        0.0 -> bright red
        0.0-0.2 -> red -> orange
        0.2-0.5 -> orange -> yellow
        0.5-0.8 -> yellow -> yellow-green
        0.8-1.0 -> yellow-green -> bright green
        """
        if retention <= 0.2:
            # red to orange
            r = 255
            g = int(255 * (retention / 0.2) * 0.5)  # fade red->orange
        elif retention <= 0.5:
            # orange to yellow
            r = 255
            g = int(128 + 127 * ((retention - 0.2) / 0.3))  # 128 -> 255
        elif retention <= 0.8:
            # yellow to yellow-green
            r = int(255 - 128 * ((retention - 0.5) / 0.3))  # 255 -> 127
            g = 255
        else:
            # yellow-green to bright green
            r = int(127 * (1 - (retention - 0.8)/0.2))  # 127 -> 0
            g = 255

        r = max(0, min(255, r))
        g = max(0, min(255, g))
        return QColor(r, g, 0)

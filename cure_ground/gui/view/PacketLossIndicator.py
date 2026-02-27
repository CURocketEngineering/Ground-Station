from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QRectF

class PacketLossIndicator(QWidget):
    def __init__(self, parent=None, height=40, segments=10):
        super().__init__(parent)
        self.retention_ratio = 1.0  # 1.0 = 100%
        self.segments = segments
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        # Colors for ranges
        self.colors = [
            (0.0, 0.3, QColor("#ff0000")),    # Red 0–30%
            (0.3, 0.5, QColor("#ff6600")),    # Orange 31–50%
            (0.5, 0.7, QColor("#ffcc00")),    # Yellow 51–70%
            (0.7, 0.9, QColor("#99cc00")),    # Yellow-Green 71–90%
            (0.9, 1.01, QColor("#00cc00")),   # Bright Green 91–100%
        ]

    def _get_color_for_ratio(self, ratio: float) -> QColor:
        for low, high, color in self.colors:
            if low <= ratio < high:
                return color
        return QColor("#cccccc")  # fallback gray

    def set_packet_loss(self, retention_ratio: float):
        """Update the current retention ratio (0.0–1.0)."""
        self.retention_ratio = max(0.0, min(1.0, retention_ratio))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        segment_width = width / self.segments

        # Determine current color based on retention
        fill_color = self._get_color_for_ratio(self.retention_ratio)

        # Calculate how many segments are filled
        filled_segments = int(self.retention_ratio * self.segments + 0.999)  # round up

        # Only draw filled segments
        for i in range(filled_segments):
            x = i * segment_width + 1
            w = segment_width - 2
            rect = QRectF(x, 1, w, height - 2)

            painter.setBrush(fill_color)
            pen = QPen(QColor("#000000"), 1)
            painter.setPen(pen)
            painter.drawRoundedRect(rect, 6, 6)

        # Draw percentage text on the last filled segment
        if filled_segments == 0:
            segment_index = 0
        else:
            segment_index = filled_segments - 1

        if filled_segments > 0:
            x = segment_index * segment_width
            rect = QRectF(x, 0, segment_width, height)
            painter.setPen(QColor("#000000"))
            painter.setFont(self.font())
            text = f"{int(self.retention_ratio * 100)}%"
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

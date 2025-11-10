from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import QTimer
import pyqtgraph as pg

class BaseGraph(QWidget):
    def __init__(self, title: str, y_label: str):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle(title)
        self.plot_widget.setLabel('left', y_label)
        self.plot_widget.setLabel('bottom', 'Time (s)')

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plot_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.layout().addWidget(self.plot_widget)

        # Graph lines (child classes set them)
        self.lines = []

        # Add legend
        self.plot_widget.addLegend()

        # Refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(200)

        self.model = None  # Set later

    def set_model(self, model):
        self.model = model

    def clear_graph(self):
        """Clears all plotted data from the graph."""
        try:
            for line in self.lines:
                line.clear()
        except:
            pass

    def update_graph(self):
        if self.model is None:
            return
        self._update_plot_data()

    def _update_plot_data(self):
        """Override in subclasses"""
        pass

class AltitudeGraph(BaseGraph):
    def __init__(self):
        super().__init__("Altitude", "Altitude (m)")
        self.line = self.plot_widget.plot(pen=pg.mkPen(width=2))
        self.lines = [self.line]

    def _update_plot_data(self):
        times, altitudes = self.model.get_graph_data()
        if len(times) > 2:
            self.line.setData(times, altitudes)


class AccelerometerGraph(BaseGraph):
    def __init__(self):
        super().__init__("Accelerometer", "Acceleration (m/s²)")

        # Three lines: X, Y, Z axes with names for legend
        self.line_x = self.plot_widget.plot(pen=pg.mkPen('r', width=2), name='Accel X')
        self.line_y = self.plot_widget.plot(pen=pg.mkPen('g', width=2), name='Accel Y')
        self.line_z = self.plot_widget.plot(pen=pg.mkPen('b', width=2), name='Accel Z')
        self.lines = [self.line_x, self.line_y, self.line_z]

    def _update_plot_data(self):
        times, ax, ay, az = self.model.get_accel_graph_data()
        if len(times) > 2:
            self.line_x.setData(times, ax)
            self.line_y.setData(times, ay)
            self.line_z.setData(times, az)
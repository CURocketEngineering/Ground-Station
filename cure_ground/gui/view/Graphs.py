from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
import pyqtgraph as pg


class BaseGraph(QWidget):
    def __init__(self, title: str, y_label: str):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle(title)
        self.plot_widget.setLabel("left", y_label)
        self.plot_widget.setLabel("bottom", "Time (s)")

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plot_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

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
        for line in self.lines:
            line.clear()

    def update_graph(self):
        if self.model is None:
            return
        self._update_plot_data()

    def _update_plot_data(self):
        """Override in subclasses"""
        pass


class MergedGraph(BaseGraph):
    def __init__(self):
        super().__init__("Flight Data", "Value")

        # --- White background + bold axes ---
        self.plot_widget.setBackground("w")

        axis = self.plot_widget.getAxis("left")
        axis.setPen(pg.mkPen(color="k", width=3))
        axis.setTextPen(pg.mkPen(color="k"))
        axis.setStyle(tickFont=pg.QtGui.QFont("Arial", 12, QFont.Weight.Bold))

        axis = self.plot_widget.getAxis("bottom")
        axis.setPen(pg.mkPen(color="k", width=3))
        axis.setTextPen(pg.mkPen(color="k"))
        axis.setStyle(tickFont=pg.QtGui.QFont("Arial", 12, QFont.Weight.Bold))

        # --- Plot lines ---
        self.alt_line = self.plot_widget.plot(
            pen=pg.mkPen(color="k", width=5), name="Altitude"
        )
        self.ax_line = self.plot_widget.plot(
            pen=pg.mkPen(color="r", width=4), name="Accel X"
        )
        self.ay_line = self.plot_widget.plot(
            pen=pg.mkPen(color="g", width=4), name="Accel Y"
        )
        self.az_line = self.plot_widget.plot(
            pen=pg.mkPen(color="b", width=4), name="Accel Z"
        )
        self.est_apogee_line = self.plot_widget.plot(
            pen=pg.mkPen(color="c", width=4), name="Estimated Apogee"
        )
        self.lines = [self.alt_line, self.ax_line, self.ay_line, self.az_line, self.est_apogee_line]

    def _update_plot_data(self):
        # Get data from model
        times, altitude = self.model.get_graph_data()
        t2, ax, ay, az = self.model.get_accel_graph_data()

        if len(times) > 2:
            self.alt_line.setData(times, altitude)

        if len(t2) > 2:
            self.ax_line.setData(t2, ax)
            self.ay_line.setData(t2, ay)
            self.az_line.setData(t2, az)

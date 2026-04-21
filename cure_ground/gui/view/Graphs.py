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

        # Replace the single-plot widget from BaseGraph with a split graph layout.
        self.layout().removeWidget(self.plot_widget)
        self.plot_widget.deleteLater()

        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.layout().addWidget(self.plot_widget)

        title = '<span style="font-size: 16pt; font-weight: 700;">Flight Data</span>'
        self.plot_widget.addLabel(title, row=0, col=0)

        self.altitude_plot = self.plot_widget.addPlot(row=1, col=0)
        self.accel_plot = self.plot_widget.addPlot(row=2, col=0)
        self.plot_widget.ci.layout.setVerticalSpacing(8)

        # Shared time axis with independent y-axes.
        self.accel_plot.setXLink(self.altitude_plot)
        self.altitude_plot.hideAxis("bottom")
        self.altitude_plot.setLabel("left", "Altitude (m)")
        self.accel_plot.setLabel("left", "Acceleration")
        self.accel_plot.setLabel("bottom", "Time (s)")

        self._style_axis(self.altitude_plot.getAxis("left"))
        self._style_axis(self.accel_plot.getAxis("left"))
        self._style_axis(self.accel_plot.getAxis("bottom"))
        self._lock_left_axis_width(width_px=110)

        self.altitude_plot.addLegend()
        self.accel_plot.addLegend()

        # --- Plot lines ---
        self.alt_line = self.altitude_plot.plot(
            pen=pg.mkPen(color="k", width=5), name="Altitude"
        )
        self.est_apogee_line = self.altitude_plot.plot(
            pen=pg.mkPen(color=(174, 0, 209), width=4), name="Estimated Apogee"
        )
        self.ax_line = self.accel_plot.plot(
            pen=pg.mkPen(color="r", width=4), name="Accel X"
        )
        self.ay_line = self.accel_plot.plot(
            pen=pg.mkPen(color="g", width=4), name="Accel Y"
        )
        self.az_line = self.accel_plot.plot(
            pen=pg.mkPen(color="b", width=4), name="Accel Z"
        )
        self.lines = [
            self.alt_line,
            self.ax_line,
            self.ay_line,
            self.az_line,
            self.est_apogee_line,
        ]

    def _style_axis(self, axis):
        axis.setPen(pg.mkPen(color="k", width=3))
        axis.setTextPen(pg.mkPen(color="k"))
        axis.setStyle(tickFont=QFont("Arial", 12, QFont.Weight.Bold))

    def _lock_left_axis_width(self, width_px: int):
        # Keep plot widths stable as y-tick label lengths change over time.
        self.altitude_plot.getAxis("left").setWidth(width_px)
        self.accel_plot.getAxis("left").setWidth(width_px)

    def _update_plot_data(self):
        # Get data from model
        times, altitude = self.model.get_graph_data()
        t2, ax, ay, az = self.model.get_accel_graph_data()

        t3, est_apogee = self.model.get_est_apogee_graph_data()

        if len(times) > 2:
            self.alt_line.setData(times, altitude)

        if len(t2) > 2:
            self.ax_line.setData(t2, ax)
            self.ay_line.setData(t2, ay)
            self.az_line.setData(t2, az)

        if len(t3) > 2:
            self.est_apogee_line.setData(t3, est_apogee)

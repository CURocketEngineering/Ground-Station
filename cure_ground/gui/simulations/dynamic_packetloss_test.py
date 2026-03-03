import sys
import random
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import os

# Ensure Python can find PacketLossIndicator
sys.path.append(os.path.abspath("../view"))

from PacketLossIndicator import PacketLossIndicator  # your dashboard class


class SmoothSignalSimulator:
    """
    Simulates signal integrity (0% to 100%) with smooth drops and recoveries.
    """

    def __init__(self, duration_seconds=10, update_interval_ms=100):
        self.duration = duration_seconds
        self.update_interval = update_interval_ms / 1000.0
        self.current_signal = 1.0  # start at 100%
        self.target_signal = 1.0

    def next_value(self):
        """
        Returns the next signal integrity value, smoothly interpolated.
        """
        # Occasionally pick a new target signal
        if random.random() < 0.02:
            # simulate a temporary obstruction
            self.target_signal = random.uniform(0.0, 0.2)
        elif random.random() < 0.05:
            # recover to high signal
            self.target_signal = random.uniform(0.9, 1.0)

        # Smooth interpolation toward target
        smoothing = 0.02  # smaller = slower, more gradual
        self.current_signal += (self.target_signal - self.current_signal) * smoothing
        self.current_signal = max(0.0, min(1.0, self.current_signal))
        return self.current_signal


def main():
    app = QApplication(sys.argv)

    # Create the packet loss indicator window
    packet_bar = PacketLossIndicator()
    packet_bar.resize(600, 60)
    packet_bar.show()

    # Create the simulator
    simulator = SmoothSignalSimulator(duration_seconds=10, update_interval_ms=100)

    # Timer updates the bar every 100 ms
    timer = QTimer()
    timer.timeout.connect(lambda: packet_bar.set_packet_loss(simulator.next_value()))
    timer.start(100)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

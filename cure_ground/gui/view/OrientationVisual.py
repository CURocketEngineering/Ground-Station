import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
import pyqtgraph.opengl as gl
from PyQt6.QtGui import QMatrix4x4

from cure_ground.gui.model.RocketModel import RocketModel
from cure_ground.core.functions.estimation.orientation import KalmanFilter
from cure_ground.gui.model.StatusModel import StatusModel


class OrientationView(QWidget):
    def __init__(self, parent=None, status_model=None):
        super().__init__(parent)

        # Ensure we have a valid StatusModel
        if status_model is None:
            status_model = StatusModel()
        self.status_model = status_model

        # Layout
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # --- 3D canvas ---
        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor("w")
        self.view.setCameraPosition(distance=3)
        self.layout.addWidget(self.view)

        # Axis and grid
        axes = gl.GLAxisItem()
        axes.setSize(1, 1, 1)
        grid = gl.GLGridItem()
        grid.setColor((200, 200, 200, 255))
        grid.scale(0.5, 0.5, 0.5)
        self.view.addItem(axes)
        self.view.addItem(grid)

        # Rocket mesh
        self.mesh = RocketModel().get_mesh()
        self.view.addItem(self.mesh)

        # --- Orientation smoothing ---
        self.current_pitch = 0.0
        self.current_yaw = 0.0
        self.current_roll = 0.0
        self.target_pitch = 0.0
        self.target_yaw = 0.0
        self.target_roll = 0.0
        self.smooth_factor = 0.1

        # Initialize filter before starting the update timer.
        self.kf = KalmanFilter()

        # Initialize sensor data safely
        self._init_sensor_data()

        # Timer for smooth updates (~60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_orientation)
        self.timer.start(100)

    @staticmethod
    def _safe_float(value, default=0.0):
        if value in (None, "", "N/A"):
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _init_sensor_data(self):
        data = getattr(self.status_model, "status_data", {})

        # Safely convert any strings to floats
        self.accel = {
            "x": self._safe_float(data.get("ACCELEROMETER_X", 0)),
            "y": self._safe_float(data.get("ACCELEROMETER_Y", 0)),
            "z": self._safe_float(data.get("ACCELEROMETER_Z", 0)),
        }
        self.gyro = {
            "x": self._safe_float(data.get("GYROSCOPE_X", 0)),
            "y": self._safe_float(data.get("GYROSCOPE_Y", 0)),
            "z": self._safe_float(data.get("GYROSCOPE_Z", 0)),
        }
        self.timestamp = self._safe_float(data.get("TIMESTAMP", 0))

    def _update_orientation(self):
        # Defensive guard in case an event reaches this callback before full init.
        if not hasattr(self, "kf"):
            self.kf = KalmanFilter()

        # Get latest sensor data
        data = getattr(self.status_model, "status_data", {})

        # Convert to floats safely
        accel = np.array(
            [
                self._safe_float(data.get("ACCELEROMETER_X", 0)),
                self._safe_float(data.get("ACCELEROMETER_Y", 0)),
                self._safe_float(data.get("ACCELEROMETER_Z", 0)),
            ]
        )
        gyro = np.array(
            [
                self._safe_float(data.get("GYROSCOPE_X", 0)),
                self._safe_float(data.get("GYROSCOPE_Y", 0)),
                self._safe_float(data.get("GYROSCOPE_Z", 0)),
            ]
        )
        timestamp = self._safe_float(data.get("TIMESTAMP", 0))

        # Run Kalman filter step
        result = self.kf.step(accel, gyro, timestamp)
        if result is None:
            return
        roll, pitch, yaw = result

        # Update target angles for smooth animation
        self.target_pitch = pitch
        self.target_roll = roll
        self.target_yaw = yaw

        # Animate mesh
        self._animate()

    # -----------------------------
    def _animate(self):
        # Smooth interpolation
        self.current_pitch += (
            self.target_pitch - self.current_pitch
        ) * self.smooth_factor
        self.current_yaw += (self.target_yaw - self.current_yaw) * self.smooth_factor
        self.current_roll += (self.target_roll - self.current_roll) * self.smooth_factor

        # Apply body-fixed rotation
        self._apply_rotation_matrix(
            self.current_pitch, self.current_yaw, self.current_roll
        )

    # -----------------------------
    def _apply_rotation_matrix(self, pitch, yaw, roll):
        # Convert degrees to radians
        p, y, r = np.radians([pitch, yaw, roll])

        # Rotation matrices (X=pitch, Y=roll, Z=yaw)
        R_x = np.array(
            [[1, 0, 0], [0, np.cos(p), -np.sin(p)], [0, np.sin(p), np.cos(p)]]
        )
        R_y = np.array(
            [[np.cos(r), 0, np.sin(r)], [0, 1, 0], [-np.sin(r), 0, np.cos(r)]]
        )
        R_z = np.array(
            [[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]]
        )

        # Body-fixed rotation: R = R_z * R_x * R_y
        R = R_z @ R_x @ R_y

        # Convert to 4x4 matrix for GLMeshItem
        M = np.eye(4)
        M[:3, :3] = R
        matrix = QMatrix4x4(*M.T.flatten())
        self.mesh.setTransform(matrix)

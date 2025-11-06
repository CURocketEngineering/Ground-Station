import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
import pyqtgraph.opengl as gl
from PyQt6.QtGui import QMatrix4x4

from cure_ground.gui.model.RocketModel import RocketModel
from cure_ground.core.functions.estimation.orientation import KalmanFilter


class OrientationView(QWidget):
    def __init__(self, parent=None, status_model=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.resize(600, 600)

        # --- 3D canvas ---
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=3)
        self.layout.addWidget(self.view)

        # Axis and grid
        axes = gl.GLAxisItem()
        axes.setSize(1, 1, 1)
        grid = gl.GLGridItem()
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

        # Timer for smooth updates (~60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_orientation)
        self.timer.start(100)

        self.data = status_model.status_data

        self.accel = {
            'x': self.data['ACCELEROMETER_X'],
            'y': self.data['ACCELEROMETER_Y'],
            'z': self.data['ACCELEROMETER_Z']
        }

        self.gyro = {
            'x': self.data['GYROSCOPE_X'],
            'y': self.data['GYROSCOPE_Y'],
            'z': self.data['GYROSCOPE_Z']
        }

        self.timestamp = self.data['TIMESTAMP']

        self.kf = KalmanFilter()


    # -----------------------------
    def _update_orientation(self):
        # Get latest sensor data
        self.data = self.status_model.status_data

        accel = {
            'x': self.data['ACCELEROMETER_X'],
            'y': self.data['ACCELEROMETER_Y'],
            'z': self.data['ACCELEROMETER_Z']
        }
        gyro = {
            'x': self.data['GYROSCOPE_X'],
            'y': self.data['GYROSCOPE_Y'],
            'z': self.data['GYROSCOPE_Z']
        }
        timestamp = self.data['TIMESTAMP']

        # Run Kalman filter step
        roll, pitch, yaw = self.kf.step(accel, gyro, timestamp)

        # Update target angles for smooth animation
        self.target_pitch = pitch
        self.target_roll = roll
        self.target_yaw = yaw

        # Animate mesh
        self._animate()

    
    # -----------------------------
    def _animate(self):
        # Smooth interpolation
        self.current_pitch += (self.target_pitch - self.current_pitch) * self.smooth_factor
        self.current_yaw += (self.target_yaw - self.current_yaw) * self.smooth_factor
        self.current_roll += (self.target_roll - self.current_roll) * self.smooth_factor

        # Apply body-fixed rotation
        self._apply_rotation_matrix(self.current_pitch, self.current_yaw, self.current_roll)

    # -----------------------------
    def _apply_rotation_matrix(self, pitch, yaw, roll):
        # Convert degrees to radians
        p, y, r = np.radians([pitch, yaw, roll])

        # Rotation matrices (X=pitch, Y=roll, Z=yaw)
        R_x = np.array([[1, 0, 0],
                        [0, np.cos(p), -np.sin(p)],
                        [0, np.sin(p), np.cos(p)]])

        R_y = np.array([[np.cos(r), 0, np.sin(r)],
                        [0, 1, 0],
                        [-np.sin(r), 0, np.cos(r)]])

        R_z = np.array([[np.cos(y), -np.sin(y), 0],
                        [np.sin(y), np.cos(y), 0],
                        [0, 0, 1]])

        # Body-fixed rotation: R = R_z * R_x * R_y
        R = R_z @ R_x @ R_y

        # Convert to 4x4 matrix for GLMeshItem
        M = np.eye(4)
        M[:3, :3] = R
        matrix = QMatrix4x4(*M.T.flatten())
        self.mesh.setTransform(matrix)
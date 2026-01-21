"""
Module for determining orientation from acceleration and gyroscopic data.
"""

import numpy as np
import time


class KalmanFilter:
    def __init__(self, Q_angle=0.001, Q_bias=1e-6, R_accel=0.03):
        # Initialize state [roll, pitch, yaw, bias_x, bias_y, bias_z]
        self.x = np.zeros(6)

        # Covariance matrix
        self.P = np.eye(6) * 0.01

        # Process noise covariance (gyro noise)
        self.Q = np.eye(6)
        self.Q[0:3, 0:3] = np.eye(3) * Q_angle
        self.Q[3:6, 3:6] *= np.eye(3) * Q_bias

        # Measurement noise covariance (accelerometer)
        self.R = np.eye(2) * R_accel

        # Measurement matrix (only roll, pitch)
        self.H = np.array([[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0]])

        self.I6 = np.eye(6)  # Identity matrix
        self.last_time = None
        self.orientation = []  # timestamped log

        # Gyro drift mitigation (small leakage to yaw)
        self.yaw_damping = 1e-4

    def step(self, accel, gyro, timestamp=None):
        # Timestamp logic
        if timestamp is None:
            timestamp = time.time()

        dt = 0.01 if self.last_time is None else timestamp - self.last_time
        self.last_time = timestamp

        # Unbiased gyro
        gyro_unbiased = gyro - self.x[3:6]

        # Prediction from gyrometer
        x_pred = self.x.copy()
        x_pred[0:3] += gyro_unbiased * dt

        # Slow yaw damping (keeps yaw bounded)
        x_pred[2] *= 1 - self.yaw_damping * dt

        # Normalize yaw to [-pi, pi]
        x_pred[2] = (x_pred[2] + np.pi) % (2 * np.pi) - np.pi

        # Predict covariance
        P_pred = self.P + self.Q * dt

        # Measurements from accelerometer
        norm = np.linalg.norm(accel)
        if norm < 1e-6:
            self.x, self.P = x_pred, P_pred
            return

        accel /= norm
        roll_acc = np.arctan2(accel[1], accel[2])
        pitch_acc = np.arctan2(-accel[0], np.sqrt(accel[1] ** 2 + accel[2] ** 2))
        z = np.array([roll_acc, pitch_acc])

        # Innovation
        y = z - self.H @ x_pred

        # Innovation covariance
        S = self.H @ P_pred @ self.H.T + self.R

        # Kalman gain
        K = P_pred @ self.H.T @ np.linalg.inv(S)

        # State & covariance update
        self.x = x_pred + K @ y
        self.P = (self.I6 - K @ self.H) @ P_pred

        # Return roll, pitch, yaw
        return np.degrees(self.x[0:3])

    def get_orientation_rad(self):
        return self.x[0:3]

    def get_orientation_deg(self):
        return np.degrees(self.x[0:3])

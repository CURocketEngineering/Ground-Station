import time
from typing import Dict, Optional, List, Tuple
from cure_ground.data_sources import DataSource
import numpy as np
from collections import deque


class GraphDataManager:
    def __init__(self, max_points: int = 5000):  # Increased for longer flights
        self.max_points = max_points

        # Altitude
        self.alt_timestamps = deque(maxlen=max_points)
        self.acl_timestamps = deque(maxlen=max_points)
        self.altitudes = deque(maxlen=max_points)

        # Accelerometer (3-axis)
        self.accel_x = deque(maxlen=max_points)
        self.accel_y = deque(maxlen=max_points)
        self.accel_z = deque(maxlen=max_points)

    # ===== ALTITUDE =====
    def add_data_point(self, altitude_value: float, timestamp: float):
        """Add a new altitude data point with timestamp in seconds"""
        try:
            alt_float = float(altitude_value)
            self.altitudes.append(alt_float)
            self.alt_timestamps.append(timestamp)
        except (ValueError, TypeError):
            pass

    # ===== ACCELEROMETER =====
    def add_accel_data_point(self, ax: float, ay: float, az: float, timestamp: float):
        """Add a new accelerometer data point (X, Y, Z)"""
        try:
            self.acl_timestamps.append(timestamp)
            self.accel_x.append(float(ax))
            self.accel_y.append(float(ay))
            self.accel_z.append(float(az))
        except (ValueError, TypeError):
            pass

    # ===== GRAPH RETRIEVAL =====
    def get_plot_data(self) -> Tuple[List[float], List[float]]:
        """Altitude data formatted for plotting"""
        return list(self.alt_timestamps), list(self.altitudes)

    def get_accel_plot_data(
        self,
    ) -> Tuple[List[float], List[float], List[float], List[float]]:
        """Accelerometer data formatted for plotting"""
        return (
            list(self.acl_timestamps),
            list(self.accel_x),
            list(self.accel_y),
            list(self.accel_z),
        )

    # ===== STATS =====
    def get_current_altitude(self) -> Optional[float]:
        return self.altitudes[-1] if self.altitudes else None

    def clear_data(self):
        """Clear all stored data"""
        self.acl_timestamps.clear()
        self.alt_timestamps.clear()
        self.altitudes.clear()
        self.accel_x.clear()
        self.accel_y.clear()
        self.accel_z.clear()

    def get_stats(self) -> Dict[str, float]:
        """Get basic statistics about the altitude data"""
        if not self.altitudes:
            return {}
        alt_list = list(self.altitudes)
        return {
            "current": alt_list[-1],
            "min": min(alt_list),
            "max": max(alt_list),
            "average": np.mean(alt_list),
        }


class StatusModel:
    def __init__(self, data_source: Optional[DataSource] = None):
        self.status_data = {}
        self.last_update_time = 0
        self.data_source = data_source
        self.graph_manager = GraphDataManager()

    def set_data_source(self, data_source: DataSource):
        self.data_source = data_source

    def update_from_data_source(self) -> bool:
        if not self.data_source or not self.data_source.is_connected():
            return False

        data = self.data_source.get_data()

        if data:
            self.status_data = data
            self.last_update_time = time.time()
            self._update_graph_data(data)
            return True

        return False

    def _update_graph_data(self, data: Dict[str, str]):
        """Extract altitude and accelerometer data and update graph manager"""
        # --- ALTITUDE ---
        altitude_keys = ["ALTITUDE", "EST_ALTITUDE", "ALT", "altitude", "alt"]
        altitude = None
        for key in altitude_keys:
            if key in data and data[key] not in ["N/A", "", None]:
                try:
                    altitude = float(data[key])
                    break
                except (ValueError, TypeError):
                    continue

        # --- ACCELEROMETER ---
        accel_keys = {
            "x": ["ACCELEROMETER_X", "AX", "accel_x", "accx", "acc_x"],
            "y": ["ACCELEROMETER_Y", "AY", "accel_y", "accy", "acc_y"],
            "z": ["ACCELEROMETER_Z", "AZ", "accel_z", "accz", "acc_z"],
        }
        ax = ay = az = None
        for axis, keys in accel_keys.items():
            for key in keys:
                if key in data and data[key] not in ["N/A", "", None]:
                    try:
                        if axis == "x":
                            ax = float(data[key])
                        elif axis == "y":
                            ay = float(data[key])
                        elif axis == "z":
                            az = float(data[key])
                        break
                    except (ValueError, TypeError):
                        continue

        # --- TIMESTAMP (convert ms → s) ---
        timestamp = None
        if "TIMESTAMP" in data and data["TIMESTAMP"] not in ["N/A", "", None]:
            try:
                timestamp = float(data["TIMESTAMP"]) / 1000.0
            except (ValueError, TypeError):
                pass

        # --- Add to buffers ---
        if timestamp is not None:
            if altitude is not None:
                self.graph_manager.add_data_point(altitude, timestamp)
            if all(v is not None for v in (ax, ay, az)):
                self.graph_manager.add_accel_data_point(ax, ay, az, timestamp)

    # ===== Graph Accessors =====
    def get_graph_data(self) -> Tuple[List[float], List[float]]:
        """Altitude graph data"""
        return self.graph_manager.get_plot_data()

    def get_accel_graph_data(
        self,
    ) -> Tuple[List[float], List[float], List[float], List[float]]:
        """Accelerometer graph data"""
        return self.graph_manager.get_accel_plot_data()

    def get_graph_stats(self) -> Dict[str, float]:
        return self.graph_manager.get_stats()

    def clear_graph_data(self):
        self.graph_manager.clear_data()

    # ===== Status Handling =====
    def update_status(self, status_data: Dict[str, str]):
        self.status_data = status_data
        self.last_update_time = time.time()

    def get_status_value(self, key: str, default: str = "N/A") -> str:
        return self.status_data.get(key, default)

    def get_all_data(self) -> Dict[str, str]:
        return self.status_data.copy()

    def get_last_update_time(self) -> float:
        return self.last_update_time

    def is_data_fresh(self, max_age_seconds: float = 5.0) -> bool:
        return (time.time() - self.last_update_time) <= max_age_seconds

import time
from typing import Dict, Optional, List, Tuple
from cure_ground.data_sources import DataSource
import numpy as np
from collections import deque


class GraphDataManager:
    def __init__(self, window_seconds: float = 40.0, safety_max_points: int = 5000):
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self.window_seconds = window_seconds
        # Backstop cap in case timestamps become unusable (e.g. all repeated/invalid).
        self.safety_max_points = safety_max_points

        # Altitude
        self.alt_timestamps = deque()
        self.altitudes = deque()

        # Accelerometer (3-axis)
        self.acl_timestamps = deque()
        self.accel_x = deque()
        self.accel_y = deque()
        self.accel_z = deque()

        # Estimated apogee
        self.est_apogee_timestamps = deque()
        self.est_apogee_values = deque()

        # Newest timestamp seen per stream, used to anchor time-window pruning.
        self._latest_alt_timestamp: Optional[float] = None
        self._latest_acl_timestamp: Optional[float] = None
        self._latest_est_apogee_timestamp: Optional[float] = None

    @staticmethod
    def _to_finite_float(value) -> Optional[float]:
        try:
            value_float = float(value)
        except (ValueError, TypeError):
            return None
        if not np.isfinite(value_float):
            return None
        return value_float

    def _is_stale_timestamp(
        self, timestamp: float, latest_timestamp: Optional[float]
    ) -> bool:
        if latest_timestamp is None:
            return False
        return timestamp < (latest_timestamp - self.window_seconds)

    @staticmethod
    def _update_latest_timestamp(
        current_latest: Optional[float], candidate: float
    ) -> float:
        if current_latest is None:
            return candidate
        return max(current_latest, candidate)

    def _maybe_reset_stream_on_timestamp_restart(
        self,
        timestamp: float,
        latest_timestamp: Optional[float],
        timestamps: deque,
        *series: deque,
    ) -> Optional[float]:
        if latest_timestamp is None:
            return latest_timestamp

        # Handle telemetry timestamp counters restarting near zero.
        restart_threshold_seconds = min(2.0, self.window_seconds)
        if (
            timestamp < latest_timestamp
            and timestamp <= restart_threshold_seconds
            and latest_timestamp >= self.window_seconds
            and (latest_timestamp - timestamp) > self.window_seconds
        ):
            timestamps.clear()
            for values in series:
                values.clear()
            return None

        return latest_timestamp

    def _prune_window(
        self, timestamps: deque, *series: deque, latest_timestamp: Optional[float]
    ):
        if latest_timestamp is None or not timestamps:
            return

        cutoff = latest_timestamp - self.window_seconds
        rows = [row for row in zip(timestamps, *series) if row[0] >= cutoff]

        if self.safety_max_points and len(rows) > self.safety_max_points:
            rows = rows[-self.safety_max_points :]

        timestamps.clear()
        for values in series:
            values.clear()

        for row in rows:
            timestamps.append(row[0])
            for idx, values in enumerate(series, start=1):
                values.append(row[idx])

    # ===== ALTITUDE =====
    def add_data_point(self, altitude_value: float, timestamp: float):
        """Add a new altitude data point with timestamp in seconds"""
        alt_float = self._to_finite_float(altitude_value)
        timestamp_float = self._to_finite_float(timestamp)
        if alt_float is None or timestamp_float is None:
            return
        self._latest_alt_timestamp = self._maybe_reset_stream_on_timestamp_restart(
            timestamp_float,
            self._latest_alt_timestamp,
            self.alt_timestamps,
            self.altitudes,
        )
        if self._is_stale_timestamp(timestamp_float, self._latest_alt_timestamp):
            return

        self._latest_alt_timestamp = self._update_latest_timestamp(
            self._latest_alt_timestamp, timestamp_float
        )
        self.altitudes.append(alt_float)
        self.alt_timestamps.append(timestamp_float)
        self._prune_window(
            self.alt_timestamps,
            self.altitudes,
            latest_timestamp=self._latest_alt_timestamp,
        )

    # ===== ESTIMATED APOGEE =====
    def add_est_apogee_point(self, est_apogee: float, timestamp: float):
        est_apogee_float = self._to_finite_float(est_apogee)
        timestamp_float = self._to_finite_float(timestamp)
        if est_apogee_float is None or timestamp_float is None:
            return
        self._latest_est_apogee_timestamp = (
            self._maybe_reset_stream_on_timestamp_restart(
                timestamp_float,
                self._latest_est_apogee_timestamp,
                self.est_apogee_timestamps,
                self.est_apogee_values,
            )
        )
        if self._is_stale_timestamp(timestamp_float, self._latest_est_apogee_timestamp):
            return

        self._latest_est_apogee_timestamp = self._update_latest_timestamp(
            self._latest_est_apogee_timestamp, timestamp_float
        )
        self.est_apogee_timestamps.append(timestamp_float)
        self.est_apogee_values.append(est_apogee_float)
        self._prune_window(
            self.est_apogee_timestamps,
            self.est_apogee_values,
            latest_timestamp=self._latest_est_apogee_timestamp,
        )

    # ===== ACCELEROMETER =====
    def add_accel_data_point(self, ax: float, ay: float, az: float, timestamp: float):
        """Add a new accelerometer data point (X, Y, Z)"""
        ax_float = self._to_finite_float(ax)
        ay_float = self._to_finite_float(ay)
        az_float = self._to_finite_float(az)
        timestamp_float = self._to_finite_float(timestamp)
        if any(v is None for v in (ax_float, ay_float, az_float, timestamp_float)):
            return
        self._latest_acl_timestamp = self._maybe_reset_stream_on_timestamp_restart(
            timestamp_float,
            self._latest_acl_timestamp,
            self.acl_timestamps,
            self.accel_x,
            self.accel_y,
            self.accel_z,
        )
        if self._is_stale_timestamp(timestamp_float, self._latest_acl_timestamp):
            return

        self._latest_acl_timestamp = self._update_latest_timestamp(
            self._latest_acl_timestamp, timestamp_float
        )
        self.acl_timestamps.append(timestamp_float)
        self.accel_x.append(ax_float)
        self.accel_y.append(ay_float)
        self.accel_z.append(az_float)
        self._prune_window(
            self.acl_timestamps,
            self.accel_x,
            self.accel_y,
            self.accel_z,
            latest_timestamp=self._latest_acl_timestamp,
        )

    # ===== GRAPH RETRIEVAL =====
    def get_plot_data(self) -> Tuple[List[float], List[float]]:
        """Altitude data formatted for plotting"""
        rows = sorted(zip(self.alt_timestamps, self.altitudes), key=lambda row: row[0])
        if not rows:
            return [], []
        times, altitudes = zip(*rows)
        return list(times), list(altitudes)

    def get_accel_plot_data(
        self,
    ) -> Tuple[List[float], List[float], List[float], List[float]]:
        """Accelerometer data formatted for plotting"""
        rows = sorted(
            zip(self.acl_timestamps, self.accel_x, self.accel_y, self.accel_z),
            key=lambda row: row[0],
        )
        if not rows:
            return [], [], [], []
        times, accel_x, accel_y, accel_z = zip(*rows)
        return list(times), list(accel_x), list(accel_y), list(accel_z)

    # ===== STATS =====
    def get_current_altitude(self) -> Optional[float]:
        return self.altitudes[-1] if self.altitudes else None

    def get_est_apogee_plot_data(self):
        rows = sorted(
            zip(self.est_apogee_timestamps, self.est_apogee_values),
            key=lambda row: row[0],
        )
        if not rows:
            return [], []
        times, est_apogee = zip(*rows)
        return list(times), list(est_apogee)

    def clear_data(self):
        """Clear all stored data"""
        self.acl_timestamps.clear()
        self.alt_timestamps.clear()
        self.altitudes.clear()
        self.accel_x.clear()
        self.accel_y.clear()
        self.accel_z.clear()
        self.est_apogee_timestamps.clear()
        self.est_apogee_values.clear()
        self._latest_alt_timestamp = None
        self._latest_acl_timestamp = None
        self._latest_est_apogee_timestamp = None

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
    def __init__(
        self, data_source: Optional[DataSource] = None, save_path: Optional[str] = None
    ):
        self.status_data = {}
        self.last_update_time = 0
        self.data_source = data_source
        self.save_path = save_path
        self.graph_manager = GraphDataManager()
        self.save_headers = []

    def set_data_source(self, data_source: DataSource):
        self.data_source = data_source

    def set_local_save_path(self, save_path: str):
        self.save_path = save_path
        # Write a CSV header
        assert hasattr(
            self.data_source, "data_names"
        ), "Data source must have 'data_names' attribute to set local save path"
        try:
            self.save_headers = self.data_source.data_names.get_name_list()
        except Exception as e:
            print(
                f"Warning: Data source does not have 'data_names' or 'get_name_list' method. CSV header will be generic. Error: {e}"
            )
            self.save_headers = []
        try:
            with open(self.save_path, "w") as f:
                f.write(",".join(self.save_headers) + "\n")
        except Exception as e:
            print(f"Error writing CSV header to {self.save_path}: {e}")

    def update_from_data_source(self) -> bool:
        if not self.data_source or not self.data_source.is_connected():
            return False

        data = self.data_source.get_data()

        if not data:
            # No new data available
            return False

        self.status_data = data
        self.last_update_time = time.time()
        self._update_graph_data(data)

        if self.save_path:
            # Save the dictionary as the next line in a CSV file
            # The first line in the CSV already has the keys as headers, so we just need to write the values in the correct order
            try:
                with open(self.save_path, "a") as f:
                    headers = self.save_headers
                    values = [str(data.get(h, "")) for h in headers]
                    f.write(",".join(values) + "\n")
            except Exception as e:
                print(f"Error saving data to {self.save_path}: {e}")
        return True

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

        # --- EST_APOGEE ---
        est_apogee_keys = ["EST_APOGEE", "EST_APOGEE_ALT", "est_apogee"]
        est_apogee = None
        for key in est_apogee_keys:
            if key in data and data[key] not in ["N/A", "", None]:
                try:
                    est_apogee = float(data[key])
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

            if est_apogee is not None:
                self.graph_manager.add_est_apogee_point(est_apogee, timestamp)

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

    def get_est_apogee_graph_data(self):
        return self.graph_manager.get_est_apogee_plot_data()

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

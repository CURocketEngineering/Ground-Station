import pandas as pd
import numpy as np
from typing import Tuple


class LaunchDetector:
    def __init__(
        self,
        threshold_g: float = 2.0,
        window_size: int = 5,
        pre_launch_seconds: int = 10,
        use_all_post_launch: bool = True,
    ):
        self.threshold_g = (
            threshold_g  # Acceleration threshold for launch detection (in G)
        )
        self.window_size = window_size  # Moving average window size
        self.pre_launch_seconds = pre_launch_seconds
        self.use_all_post_launch = (
            use_all_post_launch  # If True, uses all data after launch
        )

    def detect_launch_from_csv(
        self, csv_file_path: str
    ) -> Tuple[pd.DataFrame, int, int]:
        """
        Detect launch in CSV file and return trimmed DataFrame with launch info
        Returns: (trimmed_df, launch_index, launch_timestamp)
        """
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)

            # Find launch index
            launch_index = self._find_launch_index(df)

            if launch_index == -1:
                print("No launch detected in CSV, using full dataset")
                return df, 0, 0

            # Get timestamps and trim around launch
            trimmed_df = self._trim_around_launch(df, launch_index)

            launch_timestamp = self._get_launch_timestamp(df, launch_index)

            return trimmed_df, launch_index, launch_timestamp

        except Exception as e:
            print(f"Error processing CSV for launch detection: {e}")
            import traceback

            traceback.print_exc()
            # Fallback: return original dataframe
            df = pd.read_csv(csv_file_path)
            return df, 0, 0

    def _find_launch_index(self, df: pd.DataFrame) -> int:
        """Find the index where launch occurs based on acceleration data"""
        # Try different accelerometer column names
        accel_columns = [
            "ACCELEROMETER_Z",
            "ACCELEROMETER_X",
            "ACCELEROMETER_Y",
            "ACCLZ",
            "ACCLX",
            "ACCLY",
        ]

        accel_data = None
        for col in accel_columns:
            if col in df.columns and not df[col].isna().all():
                accel_data = pd.to_numeric(df[col], errors="coerce").fillna(0)
                break

        if accel_data is None:
            print("No accelerometer data found for launch detection")
            return -1

        # Convert to G-force (assuming data is in m/s², 1G = 9.8 m/s²)
        g_force = accel_data / 9.8

        # Apply moving average to smooth data
        g_force_smooth = (
            g_force.rolling(window=self.window_size, center=True).mean().fillna(g_force)
        )

        # Find where acceleration exceeds threshold (indicating launch)
        launch_mask = g_force_smooth > self.threshold_g

        # Find the first sustained launch event (at least 3 consecutive points above threshold)
        launch_indices = launch_mask[launch_mask].index.tolist()
        if len(launch_indices) == 0:
            print("No acceleration above threshold found")
            return -1

        # CRITICAL: Handle circular buffer wrap-around
        # Find timestamp discontinuities that indicate buffer wrap
        timestamp_columns = ["TIMESTAMP", "timestamp", "Timestamp"]
        timestamp_data = None

        for col in timestamp_columns:
            if col in df.columns and not df[col].isna().all():
                timestamp_data = pd.to_numeric(df[col], errors="coerce")
                if timestamp_data.notna().any():
                    break

        if timestamp_data is not None:
            # Find where timestamps jump backwards (circular buffer wrap point)
            time_diff = timestamp_data.diff()
            # A large negative jump indicates wrap-around
            wrap_points = time_diff[
                time_diff < -1000
            ].index.tolist()  # More than 1 second backwards

            if wrap_points:
                wrap_index = wrap_points[0]
                # Only look for launch BEFORE the wrap point (in recent data)
                launch_indices = [idx for idx in launch_indices if idx < wrap_index]

                if not launch_indices:
                    print("No launch found before circular buffer wrap point")
                    return -1

        # Find the first launch index with sustained acceleration
        for i in range(len(launch_indices) - 2):
            if (
                launch_indices[i + 1] - launch_indices[i] == 1
                and launch_indices[i + 2] - launch_indices[i + 1] == 1
            ):
                launch_index = launch_indices[i]
                return launch_index

        # Fallback: use the first launch detection
        if launch_indices:
            launch_index = launch_indices[0]
            return launch_index

        print("No sustained launch acceleration found")
        return -1

    def _get_launch_timestamp(self, df: pd.DataFrame, launch_index: int) -> float:
        """Get the timestamp of launch"""
        timestamp_columns = ["TIMESTAMP", "timestamp", "Timestamp"]

        for col in timestamp_columns:
            if col in df.columns and not df[col].isna().all():
                try:
                    timestamp = pd.to_numeric(
                        df[col].iloc[launch_index], errors="coerce"
                    )
                    if not np.isnan(timestamp):
                        return float(timestamp)
                except (ValueError, IndexError):
                    continue

        # If no timestamp found, return the index as fallback
        return float(launch_index)

    def _trim_around_launch(self, df: pd.DataFrame, launch_index: int) -> pd.DataFrame:
        """Trim dataframe to show data around launch - includes all post-launch data"""
        # Try to use timestamps for accurate trimming
        timestamp_columns = ["TIMESTAMP", "timestamp", "Timestamp"]
        timestamp_data = None
        timestamp_col = None

        for col in timestamp_columns:
            if col in df.columns and not df[col].isna().all():
                try:
                    timestamp_data = pd.to_numeric(df[col], errors="coerce")
                    if timestamp_data.notna().any():
                        timestamp_col = col
                        break
                except (ValueError, IndexError):
                    continue

        if timestamp_data is not None and timestamp_col:
            # Use timestamps for accurate time-based trimming
            launch_timestamp = timestamp_data.iloc[launch_index]

            # Calculate pre-launch bound
            pre_launch_bound = launch_timestamp - (self.pre_launch_seconds * 1000)

            # Use all data after launch if flag is set
            if self.use_all_post_launch:
                post_launch_bound = timestamp_data.max()
            else:
                post_launch_bound = timestamp_data.max()

            # Filter dataframe based on timestamps
            mask = (timestamp_data >= pre_launch_bound) & (
                timestamp_data <= post_launch_bound
            )
            trimmed_df = df[mask].copy()

            (launch_timestamp - timestamp_data[mask].min()) / 1000.0
            (timestamp_data[mask].max() - launch_timestamp) / 1000.0

        else:
            # Fallback: use index-based trimming
            total_rows = len(df)
            pre_launch_rows = min(
                launch_index, self.pre_launch_seconds * 10
            )  # Estimate 10 Hz data

            start_index = max(0, launch_index - pre_launch_rows)

            # Use all data to end of file if flag is set
            if self.use_all_post_launch:
                end_index = total_rows
                print(
                    f"Using all data from index {start_index} to end of file (row {total_rows})"
                )
            else:
                end_index = total_rows

            trimmed_df = df.iloc[start_index:end_index].copy()

        # Reset index for clean data
        trimmed_df = trimmed_df.reset_index(drop=True)
        return trimmed_df

    def create_trimmed_csv(self, original_csv_path: str, output_csv_path: str) -> bool:
        """Create a trimmed CSV file around launch"""
        try:
            trimmed_df, launch_index, launch_timestamp = self.detect_launch_from_csv(
                original_csv_path
            )

            # Save trimmed CSV
            trimmed_df.to_csv(output_csv_path, index=False)
            return True

        except Exception as e:
            print(f"Error creating trimmed CSV: {e}")
            return False

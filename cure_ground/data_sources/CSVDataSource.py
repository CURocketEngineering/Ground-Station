import csv
import time
import os
from typing import Dict, Optional, List, Tuple
from cure_ground.data_sources.DataSource import DataSource
from cure_ground.data_sources.LaunchDetector import LaunchDetector
from cure_ground.data_sources.timestamp_utils import (
    TIMESTAMP_KEYS,
    infer_timestamp_multiplier_to_ms,
    parse_timestamp_value,
    to_milliseconds,
)

from cure_ground.core.protocols.data_names.data_name_loader import (
    load_data_name_enum,
    DataNames,
)


class CSVDataSource(DataSource):
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.connected = False
        self.data_rows = []
        self.processed_rows = []
        self.current_index = 0
        self.playback_start_time = 0
        self.data_start_timestamp = 0
        self.timestamp_multiplier_to_ms = 1
        self.last_valid_values = {}
        self.trimmed_csv_path = None
        self.data_names: DataNames = load_data_name_enum(3)
        self.protocol_field_names: List[str] = []
        self.group_component_mapping: Dict[str, List[str]] = {}
        self.csv_column_mapping: Dict[str, str] = {}
        self.extra_csv_columns: List[str] = []
        self._initialize_protocol_mappings()

    def connect(self, port: str = None) -> bool:
        # Connect to CSV data source with launch detection
        try:
            # Detect launch and create trimmed data
            detector = LaunchDetector(
                pre_launch_seconds=10
            )  # REMOVED post_launch_seconds parameter

            # Create trimmed CSV in temp directory
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            original_name = os.path.basename(self.csv_file_path)
            name_without_ext = os.path.splitext(original_name)[0]
            self.trimmed_csv_path = os.path.join(
                temp_dir, f"{name_without_ext}_trimmed.csv"
            )

            success = detector.create_trimmed_csv(
                self.csv_file_path, self.trimmed_csv_path
            )

            if success and os.path.exists(self.trimmed_csv_path):
                print(f"Using trimmed CSV: {self.trimmed_csv_path}")
                used_csv_path = self.trimmed_csv_path
            else:
                print("Using original CSV (launch detection failed or not needed)")
                used_csv_path = self.csv_file_path

            # Load the CSV data (trimmed or original)
            with open(used_csv_path, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                self._build_csv_column_mapping(reader.fieldnames or [])
                self.data_rows = list(reader)

            if not self.data_rows:
                print("CSV file is empty")
                return False

            # Process the data to extract and normalize timestamps
            self._process_timestamps()
            self.current_index = 0
            self.playback_start_time = 0

            self.connected = True

            return True

        except FileNotFoundError:
            print(f"CSV file not found: {self.csv_file_path}")
            return False
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False

    def _initialize_protocol_mappings(self) -> None:
        self.protocol_field_names = []
        self.group_component_mapping = {}

        for item in self.data_names.data_definitions:
            name = item["name"]
            self.protocol_field_names.append(name)

            if item.get("type") == "group":
                component_names = []
                for component_id in item.get("data", []):
                    try:
                        component_names.append(self.data_names.get_name(component_id))
                    except KeyError:
                        continue
                self.group_component_mapping[name] = component_names

    @staticmethod
    def _normalize_column_name(name: str) -> str:
        return str(name).strip().lower()

    def _build_csv_column_mapping(self, headers: List[str]) -> None:
        self.csv_column_mapping = {}
        self.extra_csv_columns = []

        normalized_headers = {}
        for header in headers:
            normalized_headers[self._normalize_column_name(header)] = header

        for item in self.data_names.data_definitions:
            name = item["name"]
            normalized_name = self._normalize_column_name(name)
            mapped_header = normalized_headers.get(normalized_name)

            if mapped_header is None:
                normalized_id = self._normalize_column_name(str(item["id"]))
                mapped_header = normalized_headers.get(normalized_id)

            if mapped_header is not None:
                self.csv_column_mapping[name] = mapped_header

        mapped_headers = set(self.csv_column_mapping.values())
        self.extra_csv_columns = [
            header for header in headers if header not in mapped_headers
        ]

    def _read_protocol_value(
        self, row: Dict[str, str], protocol_name: str
    ) -> Tuple[Optional[str], bool]:
        column_name = self.csv_column_mapping.get(protocol_name, protocol_name)
        value = row.get(column_name)
        if value is None:
            return None, False

        cleaned_value = str(value).strip()
        if cleaned_value == "":
            return None, False
        return cleaned_value, True

    def _derive_group_value(
        self, data: Dict[str, str], group_name: str
    ) -> Optional[str]:
        component_names = self.group_component_mapping.get(group_name, [])
        if not component_names:
            return None

        component_values = []
        for component_name in component_names:
            component_value = data.get(component_name)
            if component_value in (None, "", "N/A"):
                return None
            component_values.append(component_value)

        return f"[{', '.join(component_values)}]"

    def disconnect(self) -> None:
        # Disconnect from CSV data source
        print("Disconnecting from CSV data source")
        self.connected = False
        self.data_rows = []
        self.processed_rows = []
        self.current_index = 0
        self.playback_start_time = 0
        self.data_start_timestamp = 0
        self.timestamp_multiplier_to_ms = 1
        self.last_valid_values = {}

        # Clean up trimmed CSV file if it exists
        if self.trimmed_csv_path and os.path.exists(self.trimmed_csv_path):
            try:
                os.remove(self.trimmed_csv_path)
                print(f"Cleaned up temporary file: {self.trimmed_csv_path}")
            except Exception as e:
                print(f"Error cleaning up temporary file: {e}")

    def _process_timestamps(self):
        # Process CSV data to extract and normalize timestamps
        self.processed_rows = []

        if not self.data_rows:
            return

        # Extract all valid timestamps
        valid_rows = []
        for row in self.data_rows:
            timestamp = self._extract_timestamp(row)
            if timestamp is not None:
                valid_rows.append((timestamp, row))

        if not valid_rows:
            print("No valid timestamps found in CSV")
            return

        self.timestamp_multiplier_to_ms = infer_timestamp_multiplier_to_ms(
            timestamp for timestamp, _ in valid_rows
        )
        if self.timestamp_multiplier_to_ms != 1:
            print(
                "CSVDataSource: Detected second-based timestamps, converting to milliseconds"
            )
        else:
            print("CSVDataSource: Detected millisecond-based timestamps")

        timestamp_ms_rows = [
            (
                to_milliseconds(timestamp, self.timestamp_multiplier_to_ms),
                row,
            )
            for timestamp, row in valid_rows
        ]

        # Sort by timestamp to ensure chronological order
        timestamp_ms_rows.sort(key=lambda x: x[0])

        # Find the minimum timestamp to use as baseline
        self.data_start_timestamp = timestamp_ms_rows[0][0]

        # Create processed rows with normalized timestamps
        for timestamp_ms, row in timestamp_ms_rows:
            processed_row = row.copy()
            processed_row["original_timestamp"] = timestamp_ms
            processed_row["normalized_timestamp"] = (
                timestamp_ms - self.data_start_timestamp
            )
            self.processed_rows.append(processed_row)

    def _extract_timestamp(self, row: Dict[str, str]) -> Optional[float]:
        # Extract timestamp from row
        for key in TIMESTAMP_KEYS:
            if key in row:
                timestamp = parse_timestamp_value(row[key])
                if timestamp is not None:
                    return timestamp
        return None

    def get_data(self) -> Optional[Dict[str, str]]:
        if not self.connected or not self.processed_rows:
            return None

        current_time = time.time()

        # If we haven't started playback yet, start now
        if self.playback_start_time == 0:
            self.playback_start_time = current_time
            self.current_index = 0
            # Initialize cache for carrying forward values
            self.last_valid_values = {}

        # If we've reached the end of the data
        if self.current_index >= len(self.processed_rows):
            return None

        # Calculate the elapsed time since playback started
        elapsed_time = (
            current_time - self.playback_start_time
        ) * 1000  # Convert to milliseconds

        cleaned_data = {}
        data_available = False

        # Process all rows that should have been delivered by now based on their timestamps
        while (
            self.current_index < len(self.processed_rows)
            and elapsed_time
            >= self.processed_rows[self.current_index]["normalized_timestamp"]
        ):
            current_row = self.processed_rows[self.current_index]

            # Populate protocol fields using canonical DataNames keys.
            for protocol_name in self.protocol_field_names:
                value, has_value = self._read_protocol_value(current_row, protocol_name)
                if has_value:
                    cleaned_data[protocol_name] = value
                    self.last_valid_values[protocol_name] = value
                elif protocol_name in self.last_valid_values:
                    cleaned_data[protocol_name] = self.last_valid_values[protocol_name]
                else:
                    cleaned_data[protocol_name] = "N/A"

            # Backfill group values from component values if group columns are blank.
            for group_name in self.group_component_mapping:
                if cleaned_data.get(group_name) in (None, "", "N/A"):
                    derived_group = self._derive_group_value(cleaned_data, group_name)
                    if derived_group is not None:
                        cleaned_data[group_name] = derived_group
                        self.last_valid_values[group_name] = derived_group

            # Preserve any non-protocol CSV columns so existing custom fields still flow through.
            for extra_column in self.extra_csv_columns:
                value = current_row.get(extra_column)
                if value is not None and str(value).strip() != "":
                    cleaned_value = str(value).strip()
                    cleaned_data[extra_column] = cleaned_value
                    self.last_valid_values[extra_column] = cleaned_value
                elif extra_column in self.last_valid_values:
                    cleaned_data[extra_column] = self.last_valid_values[extra_column]
                else:
                    cleaned_data[extra_column] = "N/A"

            # Include the original timestamp in the returned data
            cleaned_data["TIMESTAMP"] = str(int(current_row["original_timestamp"]))

            self.current_index += 1
            data_available = True

            # Break if we've processed all available rows for current time
            if self.current_index >= len(self.processed_rows):
                break

        return cleaned_data if data_available else None

    def is_connected(self) -> bool:
        return self.connected

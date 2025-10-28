import csv
import time
from typing import Dict, Optional, List
from .DataSource import DataSource

class CSVDataSource(DataSource):
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.connected = False
        self.data_rows = []
        self.processed_rows = []
        self.current_index = 0
        self.playback_start_time = 0
        self.data_start_timestamp = 0
        
    def connect(self, port: str = None) -> bool:
        # Connect to CSV data source
        try:
            with open(self.csv_file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                self.data_rows = list(reader)
            
            if not self.data_rows:
                print("CSV file is empty")
                return False
            
            # Process the data to extract and normalize timestamps
            self._process_timestamps()
            self.current_index = 0
            self.playback_start_time = 0
                
            self.connected = True
            
            if self.processed_rows:
                first_ts = self.processed_rows[0]['original_timestamp']
                last_ts = self.processed_rows[-1]['original_timestamp']
                total_duration = (last_ts - first_ts) / 1000.0
            
            return True
            
        except FileNotFoundError:
            print(f"CSV file not found: {self.csv_file_path}")
            return False
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
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
        
        # Sort by timestamp to ensure chronological order
        valid_rows.sort(key=lambda x: x[0])
        
        # Find the minimum timestamp to use as baseline
        self.data_start_timestamp = valid_rows[0][0]
        
        # Create processed rows with normalized timestamps
        for timestamp, row in valid_rows:
            processed_row = row.copy()
            processed_row['original_timestamp'] = timestamp
            processed_row['normalized_timestamp'] = timestamp - self.data_start_timestamp
            self.processed_rows.append(processed_row)
    
    def _extract_timestamp(self, row: Dict[str, str]) -> Optional[float]:
        # Extract timestamp from row
        timestamp_keys = ['TIMESTAMP', 'timestamp', 'Timestamp']
        
        for key in timestamp_keys:
            if key in row and row[key] and row[key] != 'N/A':
                try:
                    return float(row[key])
                except (ValueError, TypeError):
                    continue
        return None
    
    def disconnect(self) -> None:
        # Disconnect from CSV data source
        print("Disconnecting from CSV data source")
        self.connected = False
        self.data_rows = []
        self.processed_rows = []
        self.current_index = 0
        self.playback_start_time = 0
        self.data_start_timestamp = 0
        self.last_valid_values = {}  # Add this line to clear cache    
    def get_data(self) -> Optional[Dict[str, str]]:
        if not self.connected or not self.processed_rows:
            return None
        
        # If we haven't started playback yet, start now
        if self.playback_start_time == 0:
            self.playback_start_time = time.time()
            self.current_index = 0
            # Initialize cache for carrying forward values
            self.last_valid_values = {}
        
        # If we've reached the end of the data
        if self.current_index >= len(self.processed_rows):
            return None
        
        current_row = self.processed_rows[self.current_index]
        current_data_timestamp = current_row['normalized_timestamp']
        
        # Calculate how much real time has passed since playback started
        real_elapsed_time = (time.time() - self.playback_start_time) * 1000  # Convert to milliseconds
        
        # Only return data if real time has caught up to this data point's timestamp
        cleaned_data = {}
        data_available = False
        
        while real_elapsed_time >= current_data_timestamp and self.current_index < len(self.processed_rows):
            # Clean the data for display
            current_row = self.processed_rows[self.current_index]
            current_data_timestamp = current_row['normalized_timestamp']
            
            for key, value in current_row.items():
                if key in ['original_timestamp', 'normalized_timestamp']:
                    continue  # Skip internal fields
                
                # If value exists and is not empty, use it and update cache
                if value is not None and value != '':
                    cleaned_value = str(value).strip()
                    cleaned_data[key] = cleaned_value
                    self.last_valid_values[key] = cleaned_value  # Update cache
                # If value is missing but we have a cached value, use the cached value
                elif key in self.last_valid_values:
                    cleaned_data[key] = self.last_valid_values[key]
                # Otherwise, use 'N/A'
                else:
                    cleaned_data[key] = 'N/A'
            
            original_ts = current_row['original_timestamp']
            self.current_index += 1
            data_available = True
            
            # Break if we've processed all available rows for current time
            if self.current_index >= len(self.processed_rows):
                break
            current_data_timestamp = self.processed_rows[self.current_index]['normalized_timestamp']
        
        return cleaned_data if data_available else None
    
    def is_connected(self) -> bool:
        return self.connected
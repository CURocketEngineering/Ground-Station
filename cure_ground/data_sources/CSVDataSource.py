import csv
import time
from typing import Dict, Optional, List
from .DataSource import DataSource

class CSVDataSource(DataSource):
    def __init__(self, csv_file_path: str, playback_speed: float = 1.0):
        self.csv_file_path = csv_file_path
        self.playback_speed = playback_speed
        self.connected = False
        self.data_rows = []
        self.current_index = 0
        self.last_read_time = 0
        
    def connect(self) -> bool:
        # Connect to CSV data source
        try:
            with open(self.csv_file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                self.data_rows = list(reader)
            
            if not self.data_rows:
                print("CSV file is empty")
                return False
                
            self.connected = True
            self.current_index = 0
            self.last_read_time = time.time()
            print(f"Loaded {len(self.data_rows)} data rows from {self.csv_file_path}")
            return True
            
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return False
    
    def disconnect(self) -> None:
        # Disconnect from CSV data source
        self.connected = False
        self.data_rows = []
        self.current_index = 0
    
    def get_data(self) -> Optional[Dict[str, str]]:
        # Get the next data row
        if not self.connected:
            print("CSV not connected in get_data()")    # For debugging if needed
            return None
            
        if not self.data_rows:
            print("No data rows available")
            return None
        
        # Get current data row
        if self.current_index < len(self.data_rows):
            data = self.data_rows[self.current_index]
            
            # Convert empty strings to "N/A" and clean the data
            cleaned_data = {}
            for key, value in data.items():
                if value is None or value == '':
                    cleaned_data[key] = 'N/A'
                else:
                    # Convert to string and strip whitespace
                    cleaned_data[key] = str(value).strip()
            
            self.current_index += 1
            return cleaned_data
        else:
            # Loop back to beginning for continuous playback
            self.current_index = 0
            if self.data_rows:
                data = self.data_rows[self.current_index]
                
                # Convert empty strings to "N/A" for looped data too
                cleaned_data = {}
                for key, value in data.items():
                    if value is None or value == '':
                        cleaned_data[key] = 'N/A'
                    else:
                        cleaned_data[key] = str(value).strip()
                
                self.current_index += 1
                return cleaned_data
            return None    
    def is_connected(self) -> bool:
        # Check if connected to CSV data source
        return self.connected
    
    def set_playback_speed(self, speed: float):
        # Set playback speed (rows per second)
        self.playback_speed = max(0.1, speed)  # Minimum 0.1 rows per second
    
    def get_current_row(self) -> int:
        # Get current row index (for debugging)
        return self.current_index
    
    def get_total_rows(self) -> int:
        # Get total number of rows (for debugging)
        return len(self.data_rows)
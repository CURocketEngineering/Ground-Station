import csv
import time
from typing import Dict, Optional, List
from model.DataSource import DataSource

class CSVDataSource(DataSource):
    def __init__(self, csv_file_path: str, playback_speed: float = 1.0):
        self.csv_file_path = csv_file_path
        self.playback_speed = playback_speed
        self.connected = False
        self.data_rows = []
        self.current_index = 0
        self.last_read_time = 0
        
    def connect(self) -> bool:
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
        self.connected = False
        self.data_rows = []
        self.current_index = 0
    
    def get_data(self) -> Optional[Dict[str, str]]:
        if not self.connected or not self.data_rows:
            return None
        
        # Control playback speed
        current_time = time.time()
        if current_time - self.last_read_time < (1.0 / self.playback_speed):
            return None  # Wait for next interval
        
        self.last_read_time = current_time
        
        # Get current data row
        if self.current_index < len(self.data_rows):
            data = self.data_rows[self.current_index]
            self.current_index += 1
            return data
        else:
            # Loop back to beginning for continuous playback
            self.current_index = 0
            return self.data_rows[self.current_index] if self.data_rows else None
    
    def is_connected(self) -> bool:
        return self.connected
    
    def set_playback_speed(self, speed: float):
        # Set playback speed (rows per second)
        self.playback_speed = max(0.1, speed)  # Minimum 0.1 rows per second
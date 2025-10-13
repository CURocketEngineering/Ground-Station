import re
import time
from typing import Dict, Optional
from data_sources import DataSource

class StatusModel:
    def __init__(self, data_source: Optional[DataSource] = None):
        self.status_data = {}
        self.last_update_time = 0
        self.data_source = data_source
        
    def set_data_source(self, data_source: DataSource):
        # Set the data source for this model
        print(f"🔗 Setting data source in model: {type(data_source).__name__}")
        self.data_source = data_source
        
    def parse_status_data(self, status_string: str) -> Dict[str, str]:
        # Parse status data from the device response
        status = {}
        if not status_string:
            return status
            
        matches = re.findall(r"<(.*?)>(.*?)</\1>", status_string)
        
        for tag, value in matches:
            status[tag] = value.strip()
            
        return status
    
    def update_from_data_source(self) -> bool:
        # Update model from the configured data source
        print("🔄 Model: Attempting to update from data source")
        
        if not self.data_source:
            print("❌ Model: No data source set")
            return False
            
        if not self.data_source.is_connected():
            print("❌ Model: Data source not connected")
            return False
            
        data = self.data_source.get_data()
        print(f"📦 Model: Data source returned: {data}")
        
        if data:
            self.status_data = data
            self.last_update_time = time.time()
            print(f"✅ Model: Successfully updated with {len(data)} fields")
            return True
        
        print("❌ Model: Data source returned None or empty data")
        return False
    
    def update_status(self, status_data: Dict[str, str]):
        # Update the model with new status data
        self.status_data = status_data
        self.last_update_time = time.time()
    
    def get_status_value(self, key: str, default: str = "N/A") -> str:
        # Get a specific status value
        return self.status_data.get(key, default)
    
    def get_all_data(self) -> Dict[str, str]:
        # Get all status data
        return self.status_data.copy()
    
    def get_last_update_time(self) -> float:
        # Get timestamp of last update
        return self.last_update_time
    
    def is_data_fresh(self, max_age_seconds: float = 5.0) -> bool:
        # Check if data is recent
        return (time.time() - self.last_update_time) <= max_age_seconds
import re
import time
from typing import Dict, Any, Optional

class StatusModel:
    def __init__(self):
        self.status_data = {}
        self.last_update_time = 0
        
    def parse_status_data(self, status_string: str) -> Dict[str, str]:
        """Parse status data from the device response"""
        status = {}
        if not status_string:
            return status
            
        matches = re.findall(r"<(.*?)>(.*?)</\1>", status_string)
        
        for tag, value in matches:
            status[tag] = value.strip()
            
        return status
    
    def update_status(self, status_data: Dict[str, str]):
        """Update the model with new status data"""
        self.status_data = status_data
        self.last_update_time = time.time()
    
    def get_status_value(self, key: str, default: str = "N/A") -> str:
        """Get a specific status value"""
        return self.status_data.get(key, default)
    
    def get_all_data(self) -> Dict[str, str]:
        """Get all status data"""
        return self.status_data.copy()
    
    def get_last_update_time(self) -> float:
        """Get timestamp of last update"""
        return self.last_update_time
    
    def is_data_fresh(self, max_age_seconds: float = 5.0) -> bool:
        """Check if data is recent"""
        return (time.time() - self.last_update_time) <= max_age_seconds
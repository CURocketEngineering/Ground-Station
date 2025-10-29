import re
import time
from typing import Dict, Optional, List, Tuple
from data_sources import DataSource
import numpy as np
from collections import deque

class GraphDataManager:
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.timestamps = deque(maxlen=max_points)
        self.altitudes = deque(maxlen=max_points)
        self.start_time = time.time()
        
    def add_data_point(self, altitude_value: float, timestamp: Optional[float] = None):
        # Add a new altitude data point
        if timestamp is None:
            timestamp = time.time() - self.start_time
            
        try:
            alt_float = float(altitude_value)
            self.altitudes.append(alt_float)
            self.timestamps.append(timestamp)
        except (ValueError, TypeError):
            pass
    
    def get_plot_data(self) -> Tuple[List[float], List[float]]:
        # Get data formatted for plotting
        return list(self.timestamps), list(self.altitudes)
    
    def get_current_altitude(self) -> Optional[float]:
        # Get the most recent altitude value
        return self.altitudes[-1] if self.altitudes else None
    
    def clear_data(self):
        # Clear all stored data
        self.timestamps.clear()
        self.altitudes.clear()
        self.start_time = time.time()
    
    def get_stats(self) -> Dict[str, float]:
        # Get basic statistics about the altitude data
        if not self.altitudes:
            return {}
            
        alt_list = list(self.altitudes)
        return {
            'current': alt_list[-1],
            'min': min(alt_list),
            'max': max(alt_list),
            'average': np.mean(alt_list)
        }

class StatusModel:
    def __init__(self, data_source: Optional[DataSource] = None):
        self.status_data = {}
        self.last_update_time = 0
        self.data_source = data_source
        self.graph_manager = GraphDataManager()
        
    def set_data_source(self, data_source: DataSource):
        self.data_source = data_source
        
    def parse_status_data(self, status_string: str) -> Dict[str, str]:
        status = {}
        if not status_string:
            return status
            
        matches = re.findall(r"<(.*?)>(.*?)</\1>", status_string)
        
        for tag, value in matches:
            status[tag] = value.strip()
            
        return status
    
    def update_from_data_source(self) -> bool:
        if not self.data_source:
            print("No data source set")
            return False
            
        if not self.data_source.is_connected():
            print("Data source not connected")
            return False
            
        data = self.data_source.get_data()
        
        if data:
            self.status_data = data
            self.last_update_time = time.time()
            
            # Extract and store altitude data for graphing
            self._update_graph_data(data)
            return True
        
        return False
    
    def _update_graph_data(self, data: Dict[str, str]):
        # Extract altitude data and update graph manager
        altitude_keys = ['ALTITUDE', 'ALT', 'EST_ALTITUDE', 'altitude', 'alt']
        
        for key in altitude_keys:
            if key in data and data[key] not in ['N/A', '', None]:
                try:
                    altitude = float(data[key])
                    timestamp = None
                    if 'TIMESTAMP' in data:
                        try:
                            timestamp = float(data['TIMESTAMP']) / 1000.0
                        except (ValueError, TypeError):
                            pass
                    
                    self.graph_manager.add_data_point(altitude, timestamp)
                    break
                except (ValueError, TypeError):
                    continue
    
    def get_graph_data(self) -> Tuple[List[float], List[float]]:
        return self.graph_manager.get_plot_data()
    
    def get_graph_stats(self) -> Dict[str, float]:
        return self.graph_manager.get_stats()
    
    def clear_graph_data(self):
        self.graph_manager.clear_data()
    
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
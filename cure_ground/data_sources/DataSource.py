from abc import ABC, abstractmethod
from typing import Dict, Optional

class DataSource(ABC):
    # Abstract base class for all data sources
    
    @abstractmethod
    def connect(self) -> bool:
        # Connect to the data source
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        # Disconnect from the data source
        pass
    
    @abstractmethod
    def get_data(self) -> Optional[Dict[str, str]]:
        # Get the next data packet
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        # Check if connected to data source
        pass
    
    def get_type(self) -> str:
        # Return the data source type name
        return self.__class__.__name__.replace('DataSource', '').lower()
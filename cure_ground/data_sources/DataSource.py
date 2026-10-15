from abc import ABC, abstractmethod
from typing import Dict, Optional


class DataSource(ABC):
    # Abstract base class for all data sources

    @abstractmethod
    def connect(self, **kwargs) -> bool:
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

    def send_command(self, command: str) -> None:
        # Send a command to the data source
        raise NotImplementedError("send_command not implemented for this data source")

    """
    We can most likely remove this, its not needed if we create data source with factory, 
    then we should already know what type it is

    def get_type(self) -> str:
            # Return the data source type name
            return self.__class__.__name__.replace("DataSource", "").lower()
    """
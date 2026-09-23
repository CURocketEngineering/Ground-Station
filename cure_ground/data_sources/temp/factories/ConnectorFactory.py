# data_sources/DataSourceFactory.py
import time
from typing import Dict, Optional, Type, List
from ..BaseConnector import DataSource
from ..CSVConnector import CSVDataSource
from ..SerialConnector import SerialDataSource
from ..RadioConnector import RadioDataSource



class DataSourceFactory:
    """
    Class holds the available data sources and allows user to register a new data source.
    The factory is responsible for creating all types of data sources.
    """
    
    # Available data sources
    _data_sources: Dict[str, Type[DataSource]] = {
        'serial': SerialDataSource,
        'radio': RadioDataSource,
        'csv': CSVDataSource
    }
    
    @classmethod
    def get_available_types(cls) -> list:
        """
        Returns a list of the available data source types
        """
        # Get list of available data source types
        return list(cls._data_sources.keys())
    
    @classmethod
    def register_data_source(cls, name: str, data_source_class: Type[DataSource]):
        """
        Register a new data source to the factory
        """
        # Register a new data source type
        cls._data_sources[name.lower()] = data_source_class

    @classmethod
    def create_data_source(cls, input_source_type: str, **kwargs) -> Optional[DataSource]:
        """
        Return the created data source or raise an error if type does not exist
        """

        # Retrieve the data source type 
        source_type = cls._data_sources.get(input_source_type.lower())

        # If source does not exist, exit with error
        if not source_type:
            raise ValueError(f"Unknown data source type: {input_source_type}")

        # Return created data source
        return source_type(**kwargs)
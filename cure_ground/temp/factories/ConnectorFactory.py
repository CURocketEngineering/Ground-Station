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
    
    _data_sources: Dict[str, Type[DataSource]] = {
        'serial': SerialDataSource,
        'radio': RadioDataSource,
        'csv': CSVDataSource
    }
    
    @classmethod
    def get_data_source_types(cls) -> List[str]:
        """
        Returns a list of the available data source types
        """

        return list(cls._data_sources.keys())

    @classmethod
    def create_data_source(cls, input_source_type: str, **kwargs) -> DataSource:
        """
        Return the created data source or raise an error if type does not exist
        """

        source_type = cls._data_sources.get(input_source_type.lower())
        
        if source_type:
            return source_type(**kwargs)

        print(f"Invalid data source: {input_source_type}")
        
        return None
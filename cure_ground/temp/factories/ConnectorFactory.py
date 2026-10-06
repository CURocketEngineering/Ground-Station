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
    
    _DATA_SOURCES: Dict[str, Type[DataSource]] = {
        'serial': SerialDataSource,
        'radio': RadioDataSource,
        'csv': CSVDataSource
    }
    
    @classmethod
    def get_data_source_types(cls, verbose: bool = False) -> List[str]:
        """
        Returns a list of the available data source types
        """

        if verbose:
            print(f"Available data source types: {list(cls._DATA_SOURCES.keys())}")
        return list(cls._DATA_SOURCES.keys())

    @classmethod
    def create_data_source(cls, data_source_type: str, verbose: bool = False, **kwargs) -> DataSource:
        """
        Return the created data source or raise an error if type does not exist
        """

        data_source = cls._DATA_SOURCES.get(data_source_type.lower())
        
        if data_source is not None:
            if verbose:
                print(f"Creating {data_source_type} data source")
            return data_source(**kwargs)

        raise ValueError(
            f"Invalid data source: {data_source_type}. "
            f"Available data sources are: {', '.join(cls.get_data_source_types())}"
        )
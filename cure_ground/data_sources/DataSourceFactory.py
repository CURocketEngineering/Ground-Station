# data_sources/DataSourceFactory.py
import time
from typing import Dict, Type, List
from .DataSource import DataSource
from .SerialDataSource import SerialDataSource
from .CSVDataSource import CSVDataSource
from .RadioDataSource import RadioDataSource


class DataSourceFactory:
    # Factory for creating and managing data sources

    # Registry of available data source types
    _data_sources: Dict[str, Type[DataSource]] = {
        "serial": SerialDataSource,
        "csv": CSVDataSource,
        "radio": RadioDataSource,
    }

    @classmethod
    def create_data_source(cls, source_type: str, **kwargs) -> DataSource:
        # Create a data source of the specified type
        source_class = cls._data_sources.get(source_type.lower())
        if not source_class:
            raise ValueError(f"Unknown data source type: {source_type}")

        return source_class(**kwargs)

    @classmethod
    def get_available_types(cls) -> list:
        # Get list of available data source types
        return list(cls._data_sources.keys())

    @classmethod
    def register_data_source(cls, name: str, data_source_class: Type[DataSource]):
        # Register a new data source type
        cls._data_sources[name.lower()] = data_source_class

    @classmethod
    def auto_detect_source(cls, preferred_port: str = None, **kwargs) -> DataSource:
        # Try to auto-detect and create the best available data source
        available_ports = SerialDataSource().get_available_ports()

        # Filter out "No Ports Available"
        available_ports = [p for p in available_ports if p != "No Ports Available"]

        if not available_ports:
            print("No serial ports available, falling back to CSV")
            return cls.create_data_source("csv", **kwargs)

        # Try preferred port first if specified
        if preferred_port and preferred_port in available_ports:
            print(f"Trying preferred port: {preferred_port}")
            # Try radio first on preferred port
            try:
                radio_source = cls.create_data_source("radio", **kwargs)
                if radio_source.connect(preferred_port):
                    print(f"Connected to radio on {preferred_port}")
                    return radio_source
            except Exception as e:
                print(f"Failed to connect to radio on {preferred_port}: {e}")

            # Try serial on preferred port
            try:
                serial_source = cls.create_data_source("serial", **kwargs)
                if serial_source.connect(preferred_port):
                    print(f"Connected to serial device on {preferred_port}")
                    return serial_source
            except Exception as e:
                print(f"Failed to connect to serial on {preferred_port}: {e}")

        # Try all available ports for radio first (since it's more specific)
        for port in available_ports:
            if preferred_port and port != preferred_port:
                continue

            print(f"Trying radio on port: {port}")
            try:
                radio_source = cls.create_data_source("radio", **kwargs)
                if radio_source.connect(port):
                    print(f"Connected to radio on {port}")
                    return radio_source
            except Exception as e:
                print(f"Failed to connect to radio on {port}: {e}")

        # If no radio found, try generic serial on all ports
        for port in available_ports:
            if preferred_port and port != preferred_port:
                continue

            print(f"Trying serial on port: {port}")
            try:
                serial_source = cls.create_data_source("serial", **kwargs)
                if serial_source.connect(port):
                    print(f"Connected to serial device on {port}")
                    return serial_source
            except Exception as e:
                print(f"Failed to connect to serial on {port}: {e}")

        # Fall back to CSV
        print("No serial/radio devices found, falling back to CSV")
        return cls.create_data_source("csv", **kwargs)

    @classmethod
    def detect_radio_ports(cls) -> List[str]:
        # Detect which ports likely have radios connected
        radio_ports = []
        available_ports = SerialDataSource().get_available_ports()
        available_ports = [p for p in available_ports if p != "No Ports Available"]

        for port in available_ports:
            radio_source = cls.create_data_source("radio", port=port)

            if radio_source.connect():
                time.sleep(0.1)
                radio_source.disconnect()
                radio_ports.append(port)

        return radio_ports

    @classmethod
    def create_data_source_with_port(
        cls, source_type: str, port: str | None = None, **kwargs
    ) -> DataSource:
        # Create a data source and optionally connect to a specific port
        data_source = cls.create_data_source(source_type, **kwargs)

        if port and hasattr(data_source, "connect"):
            data_source.connect(port)

        return data_source

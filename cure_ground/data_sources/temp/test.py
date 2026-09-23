from cure_ground.data_sources.temp.factories import DataSourceFactory
from cure_ground.data_sources.temp import CSVDataSource, SerialDataSource, RadioDataSource


factory = DataSourceFactory()

print(factory.get_available_types())


from cure_ground.temp.factories import DataSourceFactory

factory = DataSourceFactory()

print(f"Types: {factory.get_data_source_types()}")

csv = factory.create_data_source("csv", csv_file_path="data/data_trimmed.csv")

print(f"CSV Data Source: {csv.get_type()}")


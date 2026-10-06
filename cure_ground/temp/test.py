from cure_ground.temp.factories import DataSourceFactory

factory = DataSourceFactory()

factory.get_data_source_types(verbose=True)

csv = factory.create_data_source("csv", file_path=r"cure_ground/temp/data/data_trimmed.csv", verbose=True)

print(csv.df.iloc[0:5])

from serial.tools import list_ports

ports = list_ports.comports()

for port in ports:
    print(port.device, port.description)
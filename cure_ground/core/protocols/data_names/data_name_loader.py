import yaml
import os 

class DataName:
    def __init__(self, name: str, unit: str, id: int):
        self.name = name
        self.column_name = name.lower()
        self.unit = unit
        self.id = id

class DataNames:
    def __init__(self, data_definitions: dict):
        self.data_definitions = data_definitions
        for item in data_definitions:
            self.__setattr__(item['name'], DataName(item['name'], item['unit'], item['id']))

    def get_unit(self, data_id: int) -> str:
        return self.data_definitions[data_id]["unit"]
    
    def get_name(self, data_id: int) -> str:
        return self.data_definitions[data_id]["name"]
    
    def get_name_list(self) -> list:
        return [item["name"] for item in self.data_definitions]

def load_data_name_enum(version: int) -> DataNames:
    """Load the data names from a YAML file and create an Enum"""

    # Convert the version to a 2 digit string
    # e.g. 1 -> 01
    version = str(version).zfill(2)

    yaml_path = f"cure_ground/core/protocols/data_names/data_names_v{version}.yaml"
    with open(yaml_path, "r") as file:
        data_definitions = yaml.safe_load(file)["data_names"]

    return DataNames(data_definitions)

def get_list_of_available_data_name_configs() -> list:
    """
    Get a list of available data name configurations.
    """
    folder_path = "cure_ground/core/protocols/data_names"
    files = os.listdir(folder_path)
    available_files = []
    for file in files:
        if file.endswith(".yaml"):
            version = file.split("_v")[1].split(".yaml")[0]
            available_files.append(version)
    return available_files

if __name__ == '__main__':
    """
    Example Usage:
    """
    data_names = load_data_name_enum("cure_ground/core/protocols/data_names/data_names_v01.yaml")
    print(data_names.ACCELEROMETER_X.name)
    print(data_names.get_unit(0))  # Get the unit associated with the data id of 0
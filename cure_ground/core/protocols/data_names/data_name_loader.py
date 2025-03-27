import yaml

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
    
    def get_column_name(self, data_id: int) -> str:
        return self.data_definitions[data_id]["name"].lower()

def load_data_name_enum(version: int) -> DataNames:
    """Load the data names from a YAML file and create an Enum"""

    # Convert the version to a 2 digit string
    # e.g. 1 -> 01
    version = str(version).zfill(2)

    yaml_path = f"core/protocols/data_names/data_names_v{version}.yaml"
    with open(yaml_path, "r") as file:
        data_definitions = yaml.safe_load(file)["data_names"]

    return DataNames(data_definitions)

if __name__ == '__main__':
    """
    Example Usage:
    """
    data_names = load_data_name_enum("cure_ground/core/protocols/data_names/data_names_v01.yaml")
    print(data_names.ACCELEROMETER_X.name)
    print(data_names.get_unit(0))  # Get the unit associated with the data id of 0
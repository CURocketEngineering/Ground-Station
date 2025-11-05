import os
from collections import defaultdict
from typing import Dict, List

import yaml


class DataName:
    def __init__(
        self, type: str, name: str, unit: str, id: int, data: list = None
    ):
        self.type = type
        self.name = name
        self.unit = unit
        self.id = id
        self.data = data


class DataNames:
    def __init__(self, data_definitions: List[Dict]):
        self.data_definitions = data_definitions
        self._names = {}
        self._id_to_dict = {}

        for item in data_definitions:
            self._names[item["name"]] = DataName(
                item.get("type", "single"),
                item["name"],
                item["unit"],
                item["id"],
                item.get("data", []),
            )
            self._id_to_dict[item["id"]] = item

    def __getitem__(self, name: str) -> DataName:
        """
        Grabs the DataName info for the given name
        Will raise a KeyError if the name wasn't loaded
        """

        return self._names[name]

    def get_unit(self, data_id: int) -> str:
        return self._id_to_dict[data_id]["unit"]

    def get_name(self, data_id: int) -> str:
        return self._id_to_dict[data_id]["name"]

    def get_name_list(self) -> list:
        return [item["name"] for item in self._id_to_dict.values()]

    def get_info_by_id(self, data_id: int) -> Dict:
        return self._id_to_dict[data_id]


def load_data_name_enum(version: int) -> DataNames:
    """Load the data names from a YAML file and create an Enum"""

    # Convert the version to a 2 digit string
    # e.g. 1 -> 01
    version_str = str(version).zfill(2)

    yaml_path = (
        f"cure_ground/core/protocols/data_names/data_names_v{version_str}.yaml"
    )
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


if __name__ == "__main__":
    """
    Example Usage:
    """
    data_names = load_data_name_enum(3)
    print(data_names.data_definitions)
    print(data_names["ACCELEROMETER_X"].name)
    print(
        data_names.get_unit(0)
    )  # Get the unit associated with the data id of 0

    print("ACCELEROMETER Data:")
    print(data_names["ACCELEROMETER"].name)
    print(data_names["ACCELEROMETER"].type)
    print(data_names["ACCELEROMETER"].id)
    print(data_names["ACCELEROMETER"].data)  # Should print [0, 1, 2]

    print(data_names.get_name(102))
    print(data_names.get_info_by_id(102))

import importlib
import enum
import os 

def load_states_enum(version: int) -> enum.Enum:
    """Finds the python file that contains the states enum and returns the enum object"""
    # Convert the version to a 2 digit string
    # e.g. 1 -> 01
    version = str(version).zfill(2)

    # Import the module
    module = importlib.import_module(f"core.protocols.states.states_v{version}")

    # Get the enum object
    states_enum = module.States

    return states_enum

def get_list_of_available_states_configs() -> list:
    """
    Get a list of available states configurations.
    """
    folder_path = "core/protocols/states"
    files = os.listdir(folder_path)
    available_files = []
    for file in files:
        if file.endswith(".py") and file.startswith("states_v"):
            version = file.split("_v")[1].split(".py")[0]
            available_files.append(version)
    return available_files
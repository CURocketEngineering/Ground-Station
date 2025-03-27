import importlib
import enum

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
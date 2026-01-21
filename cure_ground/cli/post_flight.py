"""
Run this on a MARTHA board that has just flown.
"""

import os

import pandas as pd
import questionary
import serial
import serial.tools.list_ports

from cure_ground.core.functions.flash_dump import flash_dump as flash_dump
from cure_ground.core.functions.plotting.basic_suite_plotly import plot_flight_data
from cure_ground.core.protocols.data_names.data_name_loader import (
    get_list_of_available_data_name_configs,
    load_data_name_enum,
)
from cure_ground.core.protocols.states.states_loader import (
    get_list_of_available_states_configs,
)


def post_flight_flow():
    data_name_options = get_list_of_available_data_name_configs()

    # Ask the user to select a data name version
    selected_version = questionary.select(
        "Select a data name version:",
        choices=data_name_options,
    ).ask()

    # Load the data names
    data_names = load_data_name_enum(selected_version)
    print(f"Loaded data names for version {selected_version}:")

    # Ask if they want to skip the dump
    skip_dump = questionary.confirm(
        "Skip the dump?",
        default=False,
    ).ask()
    if skip_dump:
        # Ask for a path a csv file
        found_csv_paths = []
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith(".csv"):
                    found_csv_paths.append(os.path.join(root, file))
        selected_csv_path = questionary.select(
            "Select a CSV file:",
            choices=found_csv_paths,
        ).ask()
        print(f"Loaded data from {selected_csv_path}")
        df = pd.read_csv(selected_csv_path)
        print(df.head())
    else:

        # Ask which COMM / tty port the board is on
        available_ports = serial.tools.list_ports.comports()
        port_options = [port.device for port in available_ports]
        selected_port = questionary.select(
            "Select a COM port:",
            choices=port_options,
        ).ask()

        # Ask if the user wants to dump all data or just until the first stop-block
        dump_all_data = questionary.confirm(
            "Dump all data?",
            default=True,
        ).ask()

        # Do the data dump
        df = flash_dump(selected_port, False, dump_all_data, data_names)
        print("\n--------------------")
        print("Data dump complete.")
        print("---------------------\n")

        if df is None:
            print("DataFrame returned is None")
            return

        print(df.head())

    # Flight name?
    flight_name = questionary.text(
        "Enter the flight name:",
        default="default_name",
    ).ask()

    save_folder = os.getcwd() + "/flight_data"
    save_folder = os.path.join(save_folder, flight_name)

    # Save the df to the save folder
    os.makedirs(save_folder, exist_ok=True)
    csv_save_path = os.path.join(save_folder, "data.csv")
    df.to_csv(csv_save_path, index=False)
    print(f"Saved data to {csv_save_path}")

    # Generate graphs?
    generate_graphs = questionary.confirm(
        "Generate graphs?",
        default=True,
    ).ask()

    # Get states version
    states_options = get_list_of_available_states_configs()
    selected_states_version = questionary.select(
        "Select a states version:",
        choices=states_options,
    ).ask()

    # Just summary?
    just_summary = questionary.confirm(
        "Just summary graph?",
        default=False,
    ).ask()

    if generate_graphs:
        graph_save_path = os.path.join(save_folder, "graphs")
        os.makedirs(graph_save_path, exist_ok=True)
        print(f"Graphs will be saved to {graph_save_path}")
        print("Generating graphs...")
        plot_flight_data(
            csv_save_path,
            graph_save_path,
            selected_version,
            selected_states_version,
            just_summary=just_summary,
        )

    print("Done!")


if __name__ == "__main__":
    post_flight_flow()

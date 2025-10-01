import os

import pandas as pd
from tqdm import tqdm

from cure_ground.core.functions.plotting.stacked_summary_plot import plot_stacked_summary_figure

# Replace with actual paths/enums if needed
from cure_ground.core.protocols.data_names.data_name_loader import load_data_name_enum
from cure_ground.core.protocols.states.states_loader import load_states

# If this file is in the same directory as common.py:
from .common import (
    create_slice_for_launch_window,
    get_launch_time,
    load_csv,
    plot_column_full_and_launch_window,
    plot_summary_figure,
    shift_timestamp_to_launch,
)


def plot_flight_data(
    csv_path: str,
    save_path: str,
    data_names_version: int,
    states_version: int,
    just_summary: bool = False,
) -> None:
    """
    Orchestrates the plotting of flight data: loads CSV, applies time shift for launch,
    plots each valid column, and generates a summary chart.

    Args:
        csv_path: Path to the CSV file containing rocket flight data.
        save_path: Directory where plots will be saved.
        data_names_version: Version number to pass to load_data_name_enum.
        states_version: Version number to pass to load_states_enum.
    """
    # 1. Load enumerations and CSV
    data_names = load_data_name_enum(data_names_version)
    states = load_states(states_version)
    df = load_csv(csv_path)
    # ALLCAPS all the column names
    df.columns = df.columns.str.upper()

    os.makedirs(save_path, exist_ok=True)

    # 2. Identify the column name for "STATE_CHANGE" and numeric code for "STATE_ASCENT"
    state_col = data_names["STATE_CHANGE"].name
    launch_state_value = states["STATE_ASCENT"].id

    # 3. Determine launch time (ms)
    launch_time_ms = get_launch_time(df, state_col, launch_state_value, data_names)

    # 4. Shift timestamps to seconds from launch
    df = shift_timestamp_to_launch(df, launch_time_ms, data_names)

    # 5. Sort by timestamp and set as index
    df.sort_values(data_names["TIMESTAMP"].name, inplace=True)
    df.set_index(data_names["TIMESTAMP"].name, inplace=True)

    # 6. Create a slice of the data from -2s to +40s for the "launch window"
    launch_df = create_slice_for_launch_window(df, start=-2, end=200)

    # 7. Gather valid columns from data definitions
    valid_columns = set(d["name"] for d in data_names.data_definitions)
    units = {d["name"]: d["unit"] for d in data_names.data_definitions}

    # 8. Plot each valid column (full data + launch window)
    if not just_summary:
        iterator = tqdm(df.columns, desc="Plotting columns", unit="column")
        for column in iterator:
            iterator.set_postfix(column=column)
            if column not in valid_columns or column == data_names["TIMESTAMP"].name:
                continue
            plot_column_full_and_launch_window(df, launch_df, column, units, save_path)

    # 9. Plot the summary figure (altitude, total accel, state changes)
    print("Plotting summary figure...")
    plot_stacked_summary_figure(
        launch_df,
        states,
        units,
        save_path,
        key_state_event_labels={
            states["STATE_ASCENT"].id: "Launch Detect",
            states["STATE_DESCENT"].id: "Apogee Detect",
        },
        data_names=data_names,
    )


# Example usage
if __name__ == "__main__":
    plot_flight_data(
        csv_path="/home/ethan/RocketClub/Ground-Station/cure_ground/flight_data/b2_irec_2025/data.csv",
        save_path="b2_irec_2025_plots",
        data_names_version=2,
        states_version=1,
        just_summary=True,
    )

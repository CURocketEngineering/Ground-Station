import os
import pandas as pd
import matplotlib.pyplot as plt

from core.protocols.data_names.data_name_loader import load_data_name_enum
from core.protocols.states.states_loader import load_states_enum


def get_launch_time(df: pd.DataFrame, state_column_name: str, launch_state: int) -> float:
    """
    Returns the timestamp (ms) of when launch occurs by 
    looking for the first row where state_column_name == launch_state,
    then reading its 'timestamp' column.
    """
    # Find the rows that match the launch_state
    launch_rows = df.loc[df[state_column_name] == launch_state, 'timestamp']
    if launch_rows.empty:
        # If no row has the launch_state, default to the earliest or raise an error
        raise ValueError(f"No row found with {state_column_name} == {launch_state}")
    # Return the first occurrence's timestamp (in ms)
    return launch_rows.iloc[0]


def plot_flight_data(csv_path: str, save_path: str, data_names_version: int, states_version: int):
    # 1. Load metadata and CSV
    data_names = load_data_name_enum(data_names_version)
    states = load_states_enum(states_version)
    df = pd.read_csv(csv_path)
    os.makedirs(save_path, exist_ok=True)

    # 2. Identify the column name for "STATE_CHANGE" and the numeric code for "STATE_ASCENT"
    state_col = data_names.STATE_CHANGE.column_name
    launch_state_value = states.STATE_ASCENT.value

    # 3. Determine launch time (ms)
    launch_time_ms = get_launch_time(df, state_col, launch_state_value)

    # 4. Convert timestamp to seconds from launch
    df['timestamp'] = (df['timestamp'] - launch_time_ms) / 1000.0

    # 5. Sort by this new 'timestamp' and set as index for easier slicing
    df.sort_values('timestamp', inplace=True)
    df.set_index('timestamp', inplace=True)

    # 6. Create a slice of the data from -2s to +40s for the "launch window"
    launch_df = df.loc[(df.index >= -2) & (df.index <= 40)].copy()

    # 7. Gather valid column names from the data definitions
    valid_columns = set(d['name'].lower() for d in data_names.data_definitions)
    units = {d['name'].lower(): d['unit'] for d in data_names.data_definitions}

    # 8. Plot each valid column
    for column in df.columns:
        # Skip columns not in the definitions or that are obviously not a data column
        if column not in valid_columns or column == 'timestamp':
            continue

        print(f"Plotting column: {column}")

        # -- Full data plot --
        plt.figure()
        plt.plot(df.index, df[column].interpolate(), linestyle='-', marker=None)
        plt.title(f"{column} (Full Data)")
        plt.xlabel("Time from Launch (s)")
        plt.ylabel(column + f" ({units[column]})")
        plt.savefig(os.path.join(save_path, f"{column}_full.png"))
        plt.close()

        # -- Launch-window plot --
        # If there's no data in launch_df for this column, the plot will just be blank.
        plt.figure()
        plt.plot(launch_df.index, launch_df[column].interpolate(), linestyle='-', marker=None)
        plt.title(f"{column} (Launch Window: -2 to +40 s)")
        plt.xlabel("Time from Launch (s)")
        plt.ylabel(column + f" ({units[column]})")
        plt.savefig(os.path.join(save_path, f"{column}_launch.png"))
        plt.close()

    # 9. Plot the state changes, altitude, and total acceleration magnitude all in one
    launch_df['total_acceleration'] = (launch_df['accelerometer_x']**2 + launch_df['accelerometer_y']**2 + launch_df['accelerometer_z']**2)**0.5
    plt.figure()
    plt.plot(launch_df.index, launch_df['altitude'].interpolate(), linestyle='-', marker=None, label='Altitude')
    plt.plot(launch_df.index, launch_df['total_acceleration'].interpolate(), linestyle='-', marker=None, label='Total Acceleration')
    
    # Find each state change (a single number gets logged when a state change happens)
    # For each non-NA value in the 'state_change' column, plot a vertical line
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
    for i, state_change in enumerate(launch_df['state_change'].dropna().index):
        label = states(launch_df.loc[state_change, 'state_change'])
        plt.axvline(state_change, color=colors[i], linestyle='--', alpha=0.5, label=label)
    
    plt.title("Altitude and Total Acceleration (Launch Window: -2 to +40 s)")
    plt.xlabel("Time from Launch (s)")
    plt.ylabel(f"Altitude ({units['altitude']}) / Total Acceleration ({units['accelerometer_x']})") 
    plt.legend()
    plt.savefig(os.path.join(save_path, "launch_summary.png"))
    plt.close()


# Example usage
if __name__ == "__main__":
    # python -m core.functions.plotting.basic_suite
    plot_flight_data(
        csv_path="../MARTHA_3-8_1.3_B1.csv",
        save_path="test_plots",
        data_names_version=1,
        states_version=1
    )

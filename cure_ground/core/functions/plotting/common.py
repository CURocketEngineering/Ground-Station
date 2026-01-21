import os

import pandas as pd
import plotly.graph_objects as go

from cure_ground.core.protocols.data_names.data_name_loader import DataNames


def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Loads CSV data into a pandas DataFrame.
    """
    return pd.read_csv(csv_path)


def get_launch_time(
    df: pd.DataFrame, state_column_name: str, launch_state: int, data_names: DataNames
) -> float:
    """
    Returns the timestamp (ms) of when launch occurs by
    looking for the first row where state_column_name == launch_state,
    then reading its 'timestamp' column.

    Args:
        df: The DataFrame containing flight data.
        state_column_name: The name of the column indicating the state.
        launch_state: The state value indicating launch.

    Returns:
        The timestamp (ms) of the launch event.
    """

    launch_rows = df.loc[df[state_column_name] == launch_state, data_names["TIMESTAMP"].name]
    if launch_rows.empty:
        raise ValueError(f"No row found with {state_column_name} == {launch_state}")
    return launch_rows.iloc[0]


def shift_timestamp_to_launch(
    df: pd.DataFrame, launch_time_ms: float, data_names: DataNames
) -> pd.DataFrame:
    """
    Subtracts the launch_time_ms from the 'timestamp' column and converts the result to seconds.

    Args:
        df: The DataFrame containing the 'timestamp' column (in ms).
        launch_time_ms: The launch time in milliseconds.

    Returns:
        A DataFrame with an updated 'timestamp' column in seconds-from-launch.
    """
    df[data_names["TIMESTAMP"].name] = (df[data_names["TIMESTAMP"].name] - launch_time_ms) / 1000.0
    return df


def create_slice_for_launch_window(
    df: pd.DataFrame, start: float = -2, end: float = 40
) -> pd.DataFrame:
    """
    Creates a slice of the data from 'start' to 'end' (in seconds), based on the DataFrame's index.

    Args:
        df: DataFrame indexed by the shifted 'timestamp' (in seconds).
        start: Start of the launch window slice.
        end: End of the launch window slice.

    Returns:
        A copy of the DataFrame containing only the rows within the specified window.
    """
    return df.loc[(df.index >= start) & (df.index <= end)].copy()


def plot_column_full_and_launch_window(
    df: pd.DataFrame, launch_df: pd.DataFrame, column: str, units: dict, save_path: str
) -> None:
    """
    Plots two time-series charts for a given column:
     1) The full dataset.
     2) The launch window subset.

    Each chart is saved as a PNG in 'save_path'.

    Args:
        df: The full DataFrame (indexed by time).
        launch_df: The launch-window subset of df.
        column: The column name in df to plot.
        units: A dict mapping column names to their respective units (e.g. {"altitude": "m"}).
        save_path: The directory path to save the PNG files.
    """
    # -- Full Data Plot --
    fig_full = go.Figure()
    fig_full.add_trace(
        go.Scatter(
            x=df.index,
            y=df[column].interpolate(),  # helps fill small NaNs
            mode="lines",
            name=column,
        )
    )
    fig_full.update_layout(
        title=f"{column} (Full Data)",
        xaxis_title="Time from Launch (s)",
        yaxis_title=f"{column} ({units.get(column, '')})",
        template="plotly_dark",
    )
    fig_full.write_image(os.path.join(save_path, f"{column}_full.png"))

    # -- Launch-Window Plot --
    fig_launch = go.Figure()
    fig_launch.add_trace(
        go.Scatter(x=launch_df.index, y=launch_df[column].interpolate(), mode="lines", name=column)
    )
    fig_launch.update_layout(
        title=f"{column} (Launch Window: -2 to +40 s)",
        xaxis_title="Time from Launch (s)",
        yaxis_title=f"{column} ({units.get(column, '')})",
        template="plotly_dark",
    )
    print("Saved a graph to ", os.path.join(save_path, f"{column}_launch.png"))
    fig_launch.write_image(os.path.join(save_path, f"{column}_launch.png"))


def plot_summary_figure(
    launch_df: pd.DataFrame,
    states,
    units: dict,
    save_path: str,
    key_state_event_labels: dict,
    data_names: DataNames,
) -> None:
    """
    Plots a summary figure for the launch window with:
     - Altitude
     - Total Acceleration
     - Vertical lines for state changes

    Saves this chart to 'launch_summary.png' in 'save_path'.

    Args:
        launch_df: The launch-window subset of the DataFrame (indexed by time).
        states: The enum-like object representing valid states (e.g., states(val).name).
        units: A dict mapping column names to units.
        save_path: The directory path for saving the summary plot.
        key_state_event_labels: A dictionary mapping state values to their labels.
    """
    # Compute total acceleration if accelerometer columns exist
    if {
        data_names["ACCELEROMETER_X"].name,
        data_names["ACCELEROMETER_Y"].name,
        data_names["ACCELEROMETER_Z"].name,
    }.issubset(launch_df.columns):
        launch_df["total_acceleration"] = (
            launch_df[data_names["ACCELEROMETER_X"].name] ** 2
            + launch_df[data_names["ACCELEROMETER_Y"].name] ** 2
            + launch_df[data_names["ACCELEROMETER_Z"].name] ** 2
        ) ** 0.5
    else:
        launch_df["total_acceleration"] = None

    fig = go.Figure()

    # Altitude trace (if available)
    if data_names["ALTITUDE"].name in launch_df.columns:
        fig.add_trace(
            go.Scatter(
                x=launch_df.index,
                y=launch_df[data_names["ALTITUDE"].name].interpolate(),
                mode="lines",
                name="Altitude",
            )
        )

    # Total Acceleration trace (if available)
    if "total_acceleration" in launch_df.columns:
        fig.add_trace(
            go.Scatter(
                x=launch_df.index,
                y=launch_df["total_acceleration"].interpolate(),
                mode="lines",
                name="Total Acceleration",
            )
        )

    # Add vertical lines for each detected state change
    if data_names["STATE_CHANGE"].name in launch_df.columns:
        state_changes = launch_df[data_names["STATE_CHANGE"].name].dropna()
        color_cycle = ["red", "lime", "blue", "cyan", "magenta", "yellow", "white", "orange"]
        for i, (idx, val) in enumerate(state_changes.items()):
            color = color_cycle[i % len(color_cycle)]
            # Attempt to retrieve the state's name from the states enum
            try:
                label = states(val).name
            except ValueError:
                label = f"State {val}"

            annotation_text = f"State: {label} ({val})"
            if val in key_state_event_labels:
                annotation_text = f"{key_state_event_labels[val]}"

            fig.add_vline(
                x=idx,
                line_width=2,
                line_dash="dash",
                line_color=color,
                annotation=dict(
                    text=annotation_text,
                    align="left",
                    font=dict(color="white"),
                    bgcolor="black",
                    bordercolor="white",
                    borderwidth=1,
                    borderpad=4,
                    showarrow=False,
                ),
            )

    if data_names["EST_APOGEE"].name in launch_df.columns:
        fig.add_trace(
            go.Scatter(
                x=launch_df.index,
                y=launch_df[data_names["EST_APOGEE"].name].interpolate(),
                mode="lines",
                name="Estimated Apogee",
            )
        )

    fig.update_layout(
        title="Altitude and Total Acceleration (Launch Window: -2 to +40 s)",
        xaxis_title="Time from Launch (s)",
        yaxis_title=(
            f"Altitude ({units.get(data_names["ALTITUDE"].name, '')}) / "
            f"Total Acceleration ({units.get(data_names["ACCELEROMETER_X"].name, '')})"
        ),
        template="plotly_dark",
    )
    # Restrict x axis start to -2 seconds
    if len(launch_df.index) > 0:
        fig.update_xaxes(range=[-2, max(launch_df.index)])
    else:
        fig.update_xaxes(range=[-2, 40])

    # Restrict the y axis to the range of 0 to the max ALTITUDE data + 5%
    if data_names["ALTITUDE"].name in launch_df.columns:
        max_altitude = launch_df[data_names["ALTITUDE"].name].max()
        fig.update_yaxes(range=[0, max_altitude * 1.05])

    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    fig.write_image(os.path.join(save_path, "launch_summary.png"))

    # Show interactive plot
    fig.show()

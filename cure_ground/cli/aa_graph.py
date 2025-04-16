import os 
import questionary
import numpy as np
import pandas as pd
from core.protocols.data_names.data_name_loader import load_data_name_enum, get_list_of_available_data_name_configs
from core.functions.plotting.basic_suite_plotly import plot_flight_data
import plotly.graph_objects as go
import plotly.subplots as sp
from tqdm import tqdm 

STATE_NAMES = { 3: "POWERED_ASCENT", 4: "COAST_ASCENT", 5: "DESCENT", } # just taking the names I want

CSV_TS_COLUMN = 0
CSV_ID_COLUMN = 1
CSV_DATA_COLUMN = 2

X_ACCEL_ID = 0
Y_ACCEL_ID = 1
Z_ACCEL_ID = 2

LAUNCH_START_TIMESTAMP = 1550000

def plot_selected_ids(csv_path, output_dir):
    df = pd.read_csv(csv_path, header=None)
    df = df[df[CSV_TS_COLUMN] >= LAUNCH_START_TIMESTAMP].copy() # new time filter

    df_alt = df[df[CSV_ID_COLUMN] == 8].copy()         
    df_fin_angle = df[df[CSV_ID_COLUMN] == 21].copy()  
    df_state_change = df[df[CSV_ID_COLUMN] == 15].copy() 

    # --- Calculate Total Acceleration --- 
    print("Calculating total acceleration...")
    # Filter only accelerometer data
    df_accel = df[df[CSV_ID_COLUMN].isin([X_ACCEL_ID, Y_ACCEL_ID, Z_ACCEL_ID])].copy()
    # Pivot to align X, Y, Z by timestamp
    df_accel_pivot = df_accel.pivot(index=CSV_TS_COLUMN, columns=CSV_ID_COLUMN, values=CSV_DATA_COLUMN)
    # Rename columns for clarity (optional but good practice)
    df_accel_pivot.rename(columns={X_ACCEL_ID: 'ax', Y_ACCEL_ID: 'ay', Z_ACCEL_ID: 'az'}, inplace=True)
    # Drop rows where any component is missing for a given timestamp
    df_accel_pivot.dropna(subset=['ax', 'ay', 'az'], inplace=True)
    # Calculate magnitude
    df_accel_pivot['total_accel'] = np.sqrt(df_accel_pivot['ax']**2 + df_accel_pivot['ay']**2 + df_accel_pivot['az']**2)
    print("Total acceleration calculated.")
    # --- End Total Acceleration Calculation ---

    fig = sp.make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter( x=df_alt[CSV_TS_COLUMN], y=df_alt[CSV_DATA_COLUMN], mode="lines", name="Altitude (m)",
        line=dict(color='deepskyblue', width = 2.5)), secondary_y=False)
    fig.add_trace(go.Scatter( x=df_fin_angle[CSV_TS_COLUMN], y=df_fin_angle[CSV_DATA_COLUMN], mode="lines", name="Fin Angle (deg)",
        line=dict(color='orangered', width=2.5)), secondary_y=False)
    fig.add_trace(go.Scatter( x=df_accel_pivot.index, y=df_accel_pivot['total_accel'], mode="lines", name="Total Accel (m/s²)",
        line=dict(color='yellow', width=2.5)), secondary_y=True)

    print("Adding state change markers...")
    y_min = df_alt[CSV_DATA_COLUMN].min() if not df_alt.empty else 0
    y_max = df_alt[CSV_DATA_COLUMN].max() if not df_alt.empty else 1

    for index, row in  tqdm(df_state_change.iterrows()):
        ts = row[CSV_TS_COLUMN]
        state_id = int(row[CSV_DATA_COLUMN])
        state_name = STATE_NAMES.get(state_id, f"State {state_id}")
        fig.add_shape(type="line", layer='below', x0=ts, x1=ts, y0=y_min, y1=y_max,
            line=dict(color='springgreen', width=2.5, dash="dash"),)
        # Add annotation
        fig.add_annotation(x=ts, y=y_max, text=state_name, showarrow=False, yshift=10, # Shift text slightly above the line
            font=dict(size=9, color="rgba(52, 52, 52, 1)"), bgcolor="lightgray")

    fig.update_layout(
        # set plot title
        title=dict(text="AARV Flight Data, 04/13/25", font=dict(color='lightgray')),

        plot_bgcolor='rgba(52, 52, 52, 1)', # halfway between darkgrey and black
        paper_bgcolor='rgba(52, 52, 52, 1)',
        font_color='lightgray', # setting default color to gray
        
        xaxis=dict( title="Timestamp (ms)",
            gridcolor='lightgray',
            linecolor='lightgray'
        ),
        yaxis=dict( title="Altitude (m) / Fin Deployment Angle (deg)",
            gridcolor='lightgray',
            linecolor='lightgray'
        ),
        yaxis2=dict( title="Total Acceleration (m/s²)",
            gridcolor='rgba(52, 52, 52, 1)',
            linecolor='rgba(52, 52, 52, 1)',
            side='right'
        ),

        legend=dict(x=0.01, y=0.99, bgcolor='lightgrey', bordercolor='grey', font=dict(color='rgba(52, 52, 52, 1)')),
        hovermode="x unified",
        xaxis_rangeslider_visible=True
    )

    save_path = os.path.join(output_dir, "aarv_flight.html") # Changed filename
    fig.write_html(save_path)
    fig.show()

    exit(1)



def main():
    data_name_options = get_list_of_available_data_name_configs()

    # Ask the user to select a data name version
    selected_version = questionary.select(
        "Select a data name version:",
        choices=data_name_options,
    ).ask()

    # Load the data names
    data_names = load_data_name_enum(selected_version)
    print(f"Loaded data names for version {selected_version}:")

    selected_csv_path = "cli/stream-18.csv"
    df = pd.read_csv(selected_csv_path)
    print(df.head())

    # Flight name?
    flight_name = "aa-test"
    save_folder = os.path.join(os.getcwd(), flight_name)

    os.makedirs(save_folder, exist_ok=True)
    csv_save_path = os.path.join(save_folder, f"{flight_name}_data.csv")
    df.to_csv(csv_save_path, index=False, header=False) # Save without header if reading with header=None
    print(f"Saved data to {csv_save_path}")

    # Generate graphs?
    generate_graphs = True # Or use questionary
    if generate_graphs:
        graph_save_path = os.path.join(save_folder, "graphs")
        os.makedirs(graph_save_path, exist_ok=True)
        plot_selected_ids(csv_save_path, graph_save_path)
        # plot_flight_data(csv_save_path, graph_save_path, selected_version, selected_states_version, just_summary=False) # If using your other plotter

    print("Done!")




if __name__ == '__main__':
    main()


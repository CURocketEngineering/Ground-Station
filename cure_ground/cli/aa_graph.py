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
    df = df[df[CSV_TS_COLUMN] >= LAUNCH_START_TIMESTAMP].copy() # time filter, starts at 1550000ms
    
    # "what data do you want?"
    df_alt = df[df[CSV_ID_COLUMN] == 8].copy()         
    df_fin_angle = df[df[CSV_ID_COLUMN] == 21].copy()  
    df_state_change = df[df[CSV_ID_COLUMN] == 15].copy() 

    # needed for starting x-axis on 0, should not be changed
    actual_start_time = df[CSV_TS_COLUMN].min()

    # --- Calculate Total Acceleration --- **ai generated
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

    # you need these so you can align your y=0 in the future
    y_min = min(0, df_alt[CSV_DATA_COLUMN].min())
    y_max = max(0, df_alt[CSV_DATA_COLUMN].max())
    y2_min = min(0, df_fin_angle[CSV_DATA_COLUMN].min(), df_accel_pivot['total_accel'].min())
    y2_max = max(0, df_fin_angle[CSV_DATA_COLUMN].max(), df_accel_pivot['total_accel'].max())

    # time from ms -> s
    df_alt['time_sec'] = (df_alt[CSV_TS_COLUMN] - actual_start_time) / 1000.0
    df_fin_angle['time_sec'] = (df_fin_angle[CSV_TS_COLUMN] - actual_start_time) / 1000.0
    df_state_change['time_sec'] = (df_state_change[CSV_TS_COLUMN] - actual_start_time) / 1000.0
    df_accel_pivot['time_sec'] = (df_accel_pivot.index - actual_start_time) / 1000.0

    fig = sp.make_subplots(specs=[[{"secondary_y": True}]]) # just makes it so a secondary axis actually exists and is a thing

    # actually graph the data read in from the csv
    fig.add_trace(go.Scatter( x=df_alt['time_sec'], y=df_alt[CSV_DATA_COLUMN], mode="lines", name="Altitude (m)",
        line=dict(color='royalblue', width = 2.5)), secondary_y=False)
    fig.add_trace(go.Scatter( x=df_fin_angle['time_sec'], y=df_fin_angle[CSV_DATA_COLUMN], mode="lines", name="Fin Angle (deg)",
        line=dict(color='#FF6347', width=2.5)), secondary_y=True)
    fig.add_trace(go.Scatter( x=df_accel_pivot['time_sec'], y=df_accel_pivot['total_accel'], mode="lines", name="Total Accel (m/s²)",
        line=dict(color='lightgreen', width=2.0, dash='dot')), secondary_y=True)

    # reading in state change logs and adding them to the graph
    for index, row in  tqdm(df_state_change.iterrows()):
        ts_sec = row['time_sec']
        state_id = int(row[CSV_DATA_COLUMN])
        state_name = STATE_NAMES.get(state_id, f"State {state_id}") # get from data structure

        # add the vertical lines for state changes, and their labels
        fig.add_shape(type="line", layer='below', x0=ts_sec, x1=ts_sec, y0=y_min, y1=y_max,
            line=dict(color='magenta', width=2.0, dash="dash"),)
        fig.add_annotation(x=ts_sec, y=y_max, text=state_name, showarrow=False, yshift=10,
            font=dict(size=9, color="magenta"), bgcolor="rgba(40, 40, 40, 0.7)")



    # ***Super important, this is basically all of the graph's styling
    fig.update_layout(
        title=dict( text="<b>AARV Flight Performance Summary</b>", font=dict(size=16, color='white'), # title colors & writing
            x=0.5, xanchor='center' ), # title pos

        plot_bgcolor='black', 
        paper_bgcolor='black', 
        font=dict(family="Arial, sans-serif", size=11, color='lightgrey'), # general font, gets overwritten in most cases

        xaxis=dict( # what does our x-axis look like?
            title=dict(text="Time Since Launch Detect (s)", font=dict(size=13)), 
            gridcolor='rgba(100, 100, 100, 0.5)', 
            linecolor='darkgrey',
            zerolinecolor='darkgrey',
            tickfont_size=11 
        ),

        yaxis=dict( # what does y-axis look like
            title=dict(text="Altitude (m)", font=dict(size=13)),
            gridcolor='rgba(100, 100, 100, 0.5)',
            linecolor='darkgrey',
            zeroline=True,
            zerolinecolor='white',
            tickfont_size=11,
            range=[y_min, y_max]
        ),

        yaxis2=dict( # what does secondary y axis look like?
            title=dict(text="Fin Angle (deg) / Total Accel (m/s²)", font=dict(size=13)),
            gridcolor='black', # matching background color, alignment is annoying and a lot of the code I did for that was ai, felt gross
            linecolor='darkgrey',
            zeroline=True,
            zerolinecolor='white',
            overlaying="y", # know that this doesn't work, it's only here for hope
            side='right',
            tickfont_size=11,
            range=[y2_min, y2_max]
        ),

        legend=dict(
            x=0.01, y=0.99,
            bgcolor='rgba(30, 30, 30, 0.8)', 
            bordercolor='grey',
            font=dict(color='white', size=10) 
        ),
        hovermode="x unified",
        xaxis_rangeslider_visible=True,
        margin=dict(l=60, r=50, t=70, b=60) 
    )


    # ending wrap up stuff
    save_path = os.path.join(output_dir, "aarv_flight.html") 
    fig.write_html(save_path)
    fig.show() # you can comment this out if you don't want the graph jumping out at you whenever you run the code

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


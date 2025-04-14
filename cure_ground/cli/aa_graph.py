import os 
import questionary
import serial
import serial.tools.list_ports
from core.protocols.data_names.data_name_loader import load_data_name_enum, get_list_of_available_data_name_configs
import core.functions.flash_dump
from core.functions.plotting.basic_suite_plotly import plot_flight_data
from core.protocols.states.states_loader import load_states_enum, get_list_of_available_states_configs
from tqdm import tqdm
import pandas as pd 
import plotly.graph_objects as go

def plot_selected_ids(csv_path, output_dir):
    df = pd.read_csv("stream-74.csv", header=None)

    """
    // State Estimation

    #define GYROSCOPE_Z 5
    #define TEMPERATURE 6
    #define PRESSURE 7
    #define ALTITUDE 8
    #define MAGNETOMETER_X 9
    #define MAGNETOMETER_Y 10
    #define MAGNETOMETER_Z 11
    #define EST_APOGEE 17
    #define EST_VERTICAL_VELOCITY 18
    #define EST_ALTITUDE 19

    """


    alt = [] 
    est_apogee = []
    fin_angle = []
    time_to_apogee = []
    # go row by row
    for i in tqdm(range(len(df))):
        # if timestamp is > 30000q
        if df.iloc[i, 0] < 20000:
            continue
        if df.iloc[i, 0] > 45000:
            break
        if df.iloc[i, 1] == 8:
            v = (
                df.iloc[i, 0], # timestamp
                df.iloc[i, 2] # data
            )
            alt.append(v)
        if df.iloc[i, 1] == 17:
            v = (
                df.iloc[i, 0], # timestamp
                df.iloc[i, 2] # data
            )
            est_apogee.append(v)
        if df.iloc[i, 1] == 21:
            v = (
                df.iloc[i, 0], # timestamp
                df.iloc[i, 2] # data
            )
            fin_angle.append(v)
        if df.iloc[i, 1] == 22:
            v = (
                df.iloc[i, 0], # timestamp
                df.iloc[i, 2] # data
            )
            time_to_apogee.append(v)

    # plot with matplot lib all of these against time
    # alt, est_apogee, fin_angle are all lists of tuples (timestamp, data)
    alt = pd.DataFrame(alt, columns=["timestamp", "data"])
    est_apogee = pd.DataFrame(est_apogee, columns=["timestamp", "data"])
    fin_angle = pd.DataFrame(fin_angle, columns=["timestamp", "data"])
    time_to_apogee = pd.DataFrame(time_to_apogee, columns=["timestamp", "data"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=alt["timestamp"], y=alt["data"], mode="lines", name="Altitude"))
    # fig.add_trace(go.Scatter(x=est_apogee["timestamp"], y=est_apogee["data"], mode="lines", name="Estimated Apogee"))
   # fig.add_trace(go.Scatter(x=fin_angle["timestamp"], y=fin_angle["data"], mode="lines", name="Fin Angle"))
    fig.add_trace(go.Scatter(x=time_to_apogee["timestamp"], y=time_to_apogee["data"], mode="lines", name="Time to Apogee"))

    fig.update_layout(title="Altitude, Estimated Apogee, and Fin Angle", xaxis_title="Timestamp", yaxis_title="Data")
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

    # Ask for a path a csv file 
    # found_csv_paths = []
    # for root, dirs, files in os.walk(os.getcwd()):
    #     for file in files:
    #         if file.endswith(".csv"):
    #             found_csv_paths.append(os.path.join(root, file))
    # selected_csv_path = questionary.select(
    #     "Select a CSV file:",
    #     choices=found_csv_paths,
    # ).ask()
    selected_csv_path = "./stream-64.csv"
    print(f"Loaded data from {selected_csv_path}")
    df = pd.read_csv(selected_csv_path)
    print(df.head())

    # Flight name?
    flight_name = "aa-test"

    save_folder = os.getcwd() + "/"
    save_folder = os.path.join(save_folder, flight_name)

    # Save the df to the save folder
    os.makedirs(save_folder, exist_ok=True)
    csv_save_path = os.path.join(save_folder, "stream-64.csv")
    df.to_csv(csv_save_path, index=False)
    print(f"Saved data to {csv_save_path}")

    # Generate graphs? 
    generate_graphs = True

    # Get states version
    # states_options = get_list_of_available_states_configs()
    # selected_states_version = questionary.select(
    #     "Select a states version:",
    #     choices=states_options,
    # ).ask()

    if generate_graphs:
        graph_save_path = os.path.join(save_folder, "graphs")
        os.makedirs(graph_save_path, exist_ok=True)
        print(f"Graphs will be saved to {graph_save_path}")
        print("Generating graphs...")
        # plot_flight_data(csv_save_path, graph_save_path, selected_version, selected_states_version, just_summary=False)
        plot_selected_ids(csv_save_path, graph_save_path)

    print("Done!")

if __name__ == '__main__':
    main()




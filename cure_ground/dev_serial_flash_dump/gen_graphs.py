import argparse 
import pandas as pd 
import matplotlib.pyplot as plt
import os 

def main(path_to_csv, first_id, ten_sec_launch):
    df = pd.read_csv(path_to_csv)
    save_path = path_to_csv.split('.')[0]+'/graphs'
    os.makedirs(save_path, exist_ok=True)

    print("number of rows: ", len(df))

    # Remove rows with a timestamp greater than 10 days
    largest_possible_timestamp = 10*24*60*60*1000
    df = df[df['timestamp'] < largest_possible_timestamp]

    print("number of rows after removing large timestamps: ", len(df))

    # Remove the first 10 seconds of data
    ten_seconds = 10*1000
    df = df[df['timestamp'] > ten_seconds]

    # Find a moment where the timestamp jumps by a negative amount (i.e. the flight id switched or a loop-back occurred)
    # This is a good place to split the data
    if first_id:
        split_index = df[df['timestamp'].diff() < 0].index[0]
        df = df.iloc[:split_index]

    # Find the launch time where state_change 
    # Launch is where state_change == 2
    launch_time = df[df['state_change'] == 2]['timestamp'].values[0]

    # Only keep data where timestamp is 2 seconds before launch and 20 seconds after launch 
    if ten_sec_launch:
        df = df[(df['timestamp'] > launch_time - 2*1000) & (df['timestamp'] < launch_time + 60*1000)]

    print("launch time: ", launch_time)
    
    # Graph every column against timestamp on separate graphs and save all to a folder
    for col in df.columns:
        if col == 'timestamp':
            continue

        df[col] = df[col].interpolate(method='linear', limit_direction='both')

        plt.plot(df['timestamp'], df[col])
        plt.title(col)
        plt.xlabel('Timestamp')
        plt.ylabel(col)
        plt.savefig(f'{save_path}/{col}.png')
        plt.close()




    print("largest timestamp: ", df['timestamp'].max())

    # Graph all the accelerometer data on the same graph
    plt.plot(df['timestamp'], df['accelerometer_x'], label='accelerometer_x')
    plt.plot(df['timestamp'], df['accelerometer_y'], label='accelerometer_y')
    plt.plot(df['timestamp'], df['accelerometer_z'], label='accelerometer_z')
    plt.title('Accelerometer Data')
    plt.xlabel('Timestamp')
    plt.ylabel('m/s^2')
    plt.legend()
    plt.savefig(f'{save_path}/accelerometer.png')
    plt.close()


    apogee_time = df[df['state_change'] == 5]['timestamp'].values[0]

    # Make timestamps in seconds T time since launch
    df['timestamp_s'] = df['timestamp'] / 1000 - launch_time / 1000
    apogee_time = apogee_time / 1000 - launch_time / 1000   # Make apogee time relative to launch time

    # Flight event graph i.e. alitemter + accelerometer + state_change vertical lines 
    plt.plot(df['timestamp_s'], df['altitude'], label='altitude')
    plt.plot(df['timestamp_s'], df['accelerometer_x'], label='accelerometer_x')
    plt.plot(df['timestamp_s'], df['accelerometer_y'], label='accelerometer_y')
    plt.plot(df['timestamp_s'], df['accelerometer_z'], label='accelerometer_z')

    # Plot predicted apogee alittude
    plt.plot(df['timestamp_s'], df['est_apogee'], label='predicted_apogee (m)')

    # Verticle line at launch time and apogee time
    plt.axvline(x=0, color='r', linestyle='--', label='launch')
    plt.axvline(x=apogee_time, color='g', linestyle='--', label='apogee')

    plt.title('Flight Event Data')
    plt.xlabel('Timestamp Since Launch (s)')
    # Have two y labels
    plt.ylabel('Altitude (m)')
    plt.ylabel('m/s^2')

    plt.legend()
    plt.savefig(f'{save_path}/flight_event.png')
    plt.show()
    plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate graphs from the CSV file')
    parser.add_argument('path_to_csv', type=str, help='Path to the CSV file')
    parser.add_argument('--first_id', action='store_true', help='If should stop once the timestamp goes backwards or flight id changes')
    parser.add_argument('--ten_sec_launch', action='store_true', help='Only graph data +- 10 seconds from launch', default=False)
    args = parser.parse_args()

    main(args.path_to_csv, args.first_id, args.ten_sec_launch)
import argparse 
import pandas as pd 
import matplotlib.pyplot as plt
import os 

def main(path_to_csv):
    df = pd.read_csv(path_to_csv)
    save_path = path_to_csv.split('.')[0]+'/graphs'
    os.makedirs(save_path, exist_ok=True)
    
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate graphs from the CSV file')
    parser.add_argument('path_to_csv', type=str, help='Path to the CSV file')
    args = parser.parse_args()

    main(args.path_to_csv)
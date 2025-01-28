import argparse
import serial 
import struct
import time 
import pandas as pd
from enum import Enum
from tqdm import tqdm 


class DataNames(Enum):
    ACCELEROMETER_X = 0
    ACCELEROMETER_Y = 1
    ACCELEROMETER_Z = 2
    GYROSCOPE_X = 3
    GYROSCOPE_Y = 4
    GYROSCOPE_Z = 5
    TEMPERATURE = 6
    PRESSURE = 7
    ALTITUDE = 8
    MAGNETOMETER_X = 9
    MAGNETOMETER_Y = 10
    MAGNETOMETER_Z = 11
    MEDIAN_ACCELERATION_SQUARED = 12
    AVERAGE_CYCLE_RATE = 13
    TIMESTAMP = 14

    def __str__(self):
        return self.name.lower()

"""
Dump spec WIP

1 byte (name as uint8_t)
4 bytes (value, either float or uint32_t) if name == 14 (decimal), then uint32_t otherwise float
1 byte ('\n' spacing, char/uint8_t)

"""

def main(port, stat_only):
    # 1. Establish connection
    ser = serial.Serial(port, 115200)

    # 1.4 clear the buffer
    print("Clearing: ", ser.read(ser.in_waiting))

    # 1.5 print out the status first
    ser.write(b'status\n')
    time.sleep(.2)
    print("Status: ")
    read = ser.read(ser.in_waiting)
    print(read)
    print(read.decode('utf-8'))

    if stat_only:
        return


    # 2. Send the command to dump the flash memory
    # Clear the incoming buffer
    while ser.in_waiting:
        print("Clearing: ", ser.read(ser.in_waiting))
    ser.write(b'dump\n')


    # 2.5 Read until we eat a \n, \r, and 's' char for alginment in that order
    a_queue = ['a', 'b', 'c']
    
    while True:
        try:
            data = ser.read(1).decode('utf-8')
        except UnicodeDecodeError:
            print("Can't decode: ", data)
        if data == a_queue[0]:
            a_queue.pop(0)
            print("Popped: ", data)
        else:
            a_queue = ['a', 'b', 'c']
            print("Failed to pop: ", data)

        if not a_queue:
            break

    print("Aligned!!!")
        


    # 3. Receive the data
    i = 0
    data_stream = []
    start_time = time.time()
    while time.time() - start_time < 10:
        # Read 6 bytes
        data = ser.read(5)
        name = data[0]
        # print(f"{i} Name: ", name, end=' ')

        # if name not in [d.value for d in DataNames]:
        #     print("Invalid name: ", name)
        #     break

        if name == 255:
            print("End of data")
            break

        if name == 14:  #uint32_t
            value = struct.unpack('<I', data[1:5])[0]
            # print("Value: ", value)
        else:  # float
            value = struct.unpack('<f', data[1:5])[0]
            # print("Value: ", value)
        
        data_stream.append((name, value))

        i += 1

    print("Processing")

    # 4. For each timestamp that is encountered, create a new row in the CSV file
    df = pd.DataFrame(columns=[str(d) for d in DataNames])
    building_row = {}
    for d in tqdm(data_stream):
        if d[0] == 14:
            if building_row:
                # print("reset")
                df = pd.concat([df, pd.DataFrame(building_row, index=[0])], ignore_index=True)
            building_row = {}
        
        # print("Adding: ", DataNames(d[0]).name.lower(), d[1])
        building_row[DataNames(d[0]).name.lower()] = d[1]

    # 5. Save the data to a CSV file
    df.to_csv('data.csv', index=False)

    print("Wrote", len(df), "rows to data.csv")


if __name__ == '__main__':
    # Capture the serial port as the command line argument
    parser = argparse.ArgumentParser(description='Dump the serial flash memory')
    parser.add_argument('port', help='The serial port to connect to')
    # Stat only
    parser.add_argument('--stat', action='store_true', help='Print the status of the device only')
    args = parser.parse_args()
    main(args.port, args.stat)
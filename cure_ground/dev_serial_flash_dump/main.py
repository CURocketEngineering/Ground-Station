import argparse
import serial 
import struct
import time 
import pandas as pd
from enum import Enum
from tqdm import tqdm 
import datetime 

# For visulazing binary data as text
import binascii

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
    STATE_CHANGE = 15
    FLIGHT_ID = 16

    def __str__(self):
        return self.name.lower()

"""
Dump spec WIP

1 byte (name as uint8_t)
4 bytes (value, either float or uint32_t) if name == 14 (decimal), then uint32_t otherwise float
1 byte ('\n' spacing, char/uint8_t)

"""

def read_all(ser):
    print("Reading from serial...")
    pages = []
    i = 0
    # Read 255 + 3 bytes per page
    while True:
        i += 1
        # time.sleep(1)
        chunk = ser.read(255 + 3)
        # print("Chunk: ", chunk)
        if chunk[:3] == b"lsh":
            # print("LSH")
            pages.append(chunk[3:])
        elif b'EOF' in chunk:
            print("\nEOF: ", chunk)
            break
        else:
            print("\nInvalid chunk: ", chunk)
            break
        if i % 16 == 0:
            print("Read: ", len(pages), "pages", end='\r')

        # Send the 'n' to get the next page
        ser.write(b'n')
    print("\nREAD ALL DONE")
    return pages

def main(port, stat_only, all_data):
    # 1. Establish connection
    ser = serial.Serial(port, 115200)

    # 1.4 clear the buffer
    time.sleep(.1)
    while ser.in_waiting:
        print("Clearing: ", len(ser.read(ser.in_waiting)), "bytes")
        ser.read(ser.in_waiting)
        time.sleep(.1)

    # 1.5 print out the status first
    ser.write(b'status\n')
    time.sleep(.2)
    print("Status: ")
    read = ser.read(ser.in_waiting)
    print(read.decode('utf-8'))
    

    if stat_only:
        return


    # 2. Send the command to dump the flash memory
    # Clear the incoming buffer
    while ser.in_waiting:
        print("Clearing: ", ser.read(ser.in_waiting))

    if all_data:
        ser.write(b'dump -a\n')
    else:
        ser.write(b'dump\n')


    # 2.5 Read until we eat a \n, \r, and 's' char for alginment in that order
    a_queue = ['a', 'b', 'c', 'd', 'e', 'f']
    
    while True:
        try:
            data = ser.read(1).decode('utf-8')
        except UnicodeDecodeError:
            print("Can't decode: ", data)
        if data == a_queue[0]:
            a_queue.pop(0)
            # print("Popped: ", data)
        else:
            a_queue = ['a', 'b', 'c', 'd', 'e', 'f']
            # print("Failed to pop: ", data)

        if not a_queue:
            break

    print("Aligned!!!")
        


    # 3. Receive the data
    all_pages = read_all(ser)
    
    # 3.5 Parse the data
    data_stream = []

    print("Number of pages: ", len(all_pages))

    for page in all_pages:
        for i in range(0, len(page), 5):
            # print("i: ", i, "page len: ", len(page))
            name = page[i]
            value = page[i+1:i+5]
            # print(len(value))
            if name == 14:
                value = struct.unpack('<I', value)[0]
            else:
                value = struct.unpack('<f', value)[0]
            data_stream.append((name, value))



    print()
    print("Processing")

    # 4. For each timestamp that is encountered, create a new row in the CSV file
    rows = []
    building_row = {}
    for d in tqdm(data_stream):
        if d[0] == DataNames.TIMESTAMP.value:
            # Time to start a new row.
            if building_row:  # Only add non-empty rows.
                rows.append(building_row)
            building_row = {}
        try:
            # Use the enum's name (or however you want to map it)
            key = DataNames(d[0]).name.lower()
            building_row[key] = d[1]
        except ValueError:
            print("Invalid name: ", d[0])
            # Optionally, break or continue

    # Add the final row if it exists.
    if building_row:
        rows.append(building_row)

    expected_columns = [str(d) for d in DataNames]
    df = pd.DataFrame(rows, columns=expected_columns)


    # Data name
    data_name = "flight_data_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".csv"
    # 5. Save the data to a CSV file
    df.to_csv(data_name, index=False)

    print("Wrote", len(df), "rows to", data_name)
    print("Latest timestamp: ", df['timestamp'].iloc[-1])
    print("Greatest timestamp: ", df['timestamp'].max())
    print("Smallest timestamp: ", df['timestamp'].min())


if __name__ == '__main__':
    # Capture the serial port as the command line argument
    parser = argparse.ArgumentParser(description='Dump the serial flash memory')
    parser.add_argument('port', help='The serial port to connect to')
    # Stat only
    parser.add_argument('--stat', action='store_true', help='Print the status of the device only')
    parser.add_argument('-a', '--all', action='store_true', help='Dump all the data, ignoring empty pages')
    args = parser.parse_args()
    main(args.port, args.stat, args.all)
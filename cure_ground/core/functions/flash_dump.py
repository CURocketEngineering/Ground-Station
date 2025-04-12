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

def main(port, stat_only, all_data, DataNames):
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
        if d[0] == DataNames.TIMESTAMP.id:
            # Time to start a new row.
            if building_row:  # Only add non-empty rows.
                rows.append(building_row)
            building_row = {}
        try:
            # Use the enum's name (or however you want to map it)
            key = DataNames.get_name(d[0])
            building_row[key] = d[1]
        except ValueError:
            print("Invalid name: ", d[0])
            # Optionally, break or continue

    # Add the final row if it exists.
    if building_row:
        rows.append(building_row)

    expected_columns = DataNames.get_name_list()
    df = pd.DataFrame(rows, columns=expected_columns)


    return df 
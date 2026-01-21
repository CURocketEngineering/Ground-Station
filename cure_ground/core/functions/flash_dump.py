# For visulazing binary data as text
import struct
import time

import pandas as pd
import serial
from tqdm import tqdm

from cure_ground.core.protocols.data_names.data_name_loader import DataNames

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
        elif b"EOF" in chunk:
            print("\nEOF: ", chunk)
            break
        else:
            print("\nInvalid chunk: ", chunk)
            break
        if i % 16 == 0:
            print("Read: ", len(pages), "pages", end="\r")

        # Send the 'n' to get the next page
        ser.write(b"n")
    print("\nREAD ALL DONE")
    return pages


def flash_dump(port: str, stat_only: bool, all_data: bool, date_names: DataNames):
    """
    Dumps flight data from the rocket's flash memory via serial communication.

    This function establishes a serial connection to the rocket's onboard system and
    retrieves stored flight data from flash memory. The data is parsed according to
    a binary protocol where each data point consists of:
    - 1 byte: data type identifier (uint8_t)
    - 4 bytes: value (float or uint32_t depending on data type)
    - Optional newline spacing

    The function handles data alignment, reads paginated data from the device,
    and converts the binary stream into a structured pandas DataFrame.

    Args:
        port (str): Serial port identifier (e.g., '/dev/ttyUSB0' or 'COM3')
        stat_only (bool): If True, only retrieves and displays device status
                         without dumping flash data
        all_data (bool): If True, dumps all data from flash memory using 'dump -a'
                        command. If False, uses standard 'dump' command
        date_names (DataNames): Data names configuration object containing
                               mappings between data IDs and their corresponding
                               names, units, and column definitions

    Returns:
        pandas.DataFrame or None: A DataFrame containing the flight data with columns
                                 corresponding to the data names defined in date_names.
                                 Returns None if stat_only is True.

    Raises:
        serial.SerialException: If serial port cannot be opened or communication fails
        struct.error: If binary data cannot be unpacked properly
        UnicodeDecodeError: If alignment data cannot be decoded

    Protocol Details:
        - Baud rate: 115200
        - Data format: Binary, little-endian
        - Page size: 255 bytes + 3 byte header
        - Alignment sequence: 'abcdef'
        - Timestamp ID: 14 (triggers new row creation)
        - End marker: 'EOF' in data stream

    Example:
        >>> from cure_ground.core.protocols.data_names.data_name_loader import load_data_name_enum
        >>> data_names = load_data_name_enum(1)
        >>> df = flash_dump('/dev/ttyUSB0', stat_only=False, all_data=True, date_names=data_names)
        >>> print(df.head())
    """
    # 1. Establish connection
    ser = serial.Serial(port, 115200)

    # 1.4 clear the buffer
    time.sleep(0.1)
    while ser.in_waiting:
        print("Clearing: ", len(ser.read(ser.in_waiting)), "bytes")
        ser.read(ser.in_waiting)
        time.sleep(0.1)

    # 1.5 print out the status first
    ser.write(b"status\n")
    time.sleep(0.2)
    print("Status: ")
    read = ser.read(ser.in_waiting)
    print(read.decode("utf-8"))

    if stat_only:
        return

    # 2. Send the command to dump the flash memory
    # Clear the incoming buffer
    while ser.in_waiting:
        print("Clearing: ", ser.read(ser.in_waiting))

    if all_data:
        ser.write(b"dump -a\n")
    else:
        ser.write(b"dump\n")

    # 2.5 Read until we eat a \n, \r, and 's' char for alginment in that order
    a_queue = ["a", "b", "c", "d", "e", "f"]

    while True:
        try:
            data = ser.read(1).decode("utf-8")
        except UnicodeDecodeError:
            print("Failed to decode last byte")
            continue
        if data == a_queue[0]:
            a_queue.pop(0)
            # print("Popped: ", data)
        else:
            a_queue = ["a", "b", "c", "d", "e", "f"]
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
            value = page[i + 1 : i + 5]
            # print(len(value))
            if name == 14:
                value = struct.unpack("<I", value)[0]
            else:
                value = struct.unpack("<f", value)[0]
            data_stream.append((name, value))

    print()
    print("Processing")

    # 4. For each timestamp that is encountered, create a new row in the CSV file
    rows = []
    building_row = {}
    for d in tqdm(data_stream):
        if d[0] == date_names["TIMESTAMP"].id:
            # Time to start a new row.
            if building_row:  # Only add non-empty rows.
                rows.append(building_row)
            building_row = {}
        try:
            # Use the enum's name (or however you want to map it)
            key = date_names.get_name(d[0])
            building_row[key] = d[1]
        except ValueError:
            print("Invalid name: ", d[0])
            # Optionally, break or continue

    # Add the final row if it exists.
    if building_row:
        rows.append(building_row)

    expected_columns = date_names.get_name_list()
    df = pd.DataFrame(rows, columns=expected_columns)

    return df

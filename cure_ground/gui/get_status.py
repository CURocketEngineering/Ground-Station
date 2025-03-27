import serial
import time
import re
from typing import Dict


def get_status(port) -> Dict[str, str]:
    # 1. Establish connection
    ser = serial.Serial(port, 115200)

    # 1.4 Clear the buffer
    time.sleep(0.1)
    while ser.in_waiting:
        print("Clearing: ", len(ser.read(ser.in_waiting)), "bytes")
        ser.read(ser.in_waiting)
        time.sleep(0.1)

    # 1.5 Print out the status first
    ser.write(b'getstatus\n')
    time.sleep(0.2)
    # print("Status: ")
    
    # Read the incoming data
    read = ser.read(ser.in_waiting)
    stat_str = read.decode('utf-8')
    # print(stat_str)

    # Create an empty dictionary for parsed data
    status = {}

    # Use regex to find all tag-value pairs
    matches = re.findall(r"<(.*?)>(.*?)</\1>", stat_str)

    # Populate the dictionary with parsed tag-value pairs
    for tag, value in matches:
        status[tag] = value.strip()

    return status


if __name__ == "__main__":
    port_name = "COM4"
    status_dict = get_status(port_name)
    
    # Print the dictionary to verify
    print("\nParsed Status Dictionary:")
    for key, value in status_dict.items():
        print(f"{key}: {value}")

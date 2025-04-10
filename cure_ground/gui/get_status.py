import serial
import time
import re
from typing import Dict


def get_status(port) -> Dict[str, str]:
    # 1. Establish connection
    try:
        ser = serial.Serial(port, 115200)
    except Exception as e:
        print(f"Error opening serial port: {e}")
        return {}

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


def clear_post_launch_mode(port) -> bool:
    """Send command to clear post-launch mode"""
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(0.1)  # Wait for connection
        
        # Send the clear command
        ser.write(b'clear_plm\n')
        time.sleep(0.2)  # Wait for response
        
        # Read acknowledgment (optional)
        response = ser.read(ser.in_waiting).decode('utf-8').strip()
        ser.close()
        
        return True  # Assume success unless exception occurs
    except Exception as e:
        print(f"Error clearing post-launch mode: {e}")
        return False


if __name__ == "__main__":
    port_name = "COM4"
    status_dict = get_status(port_name)
    
    # Print the dictionary to verify
    print("\nParsed Status Dictionary:")
    for key, value in status_dict.items():
        print(f"{key}: {value}")

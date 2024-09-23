# Listen to serial on /dev/ttyACM0

import serial
import time
import sys
import os
import json

print("cwd: ", os.getcwd())

from protocols.commands import commands_v01


def CURE_ping(ser, timeout=10):
    # Create a 4 byte packet
    # '<' 0x01 0x00 '>'
    packet = b'<\x01\x00>'

    # Send the packet
    print("Pinging...")
    ser.write(packet)

    # Wait for a response
    start_time = time.time()
    while ser.in_waiting < 4:
        if time.time() - start_time > timeout:
            print("Timeout waiting for response")

    # Read the response
    packet = ser.read(4)

    # Check if its the ping
    if packet == b'<\x01\x00>':
        print("Ping response received")
        return True 
    
    return False


def main():
    # Open serial port
    ser = serial.Serial('/dev/ttyACM0', 115200)
    ser.flushInput()

    # Read serial data
    while True:
        try:
            CURE_ping(ser)
            time.sleep(1)


        except KeyboardInterrupt:
            ser.close()
            print("Exiting program")
            break

    ser.close()


if __name__ == "__main__":
    main()
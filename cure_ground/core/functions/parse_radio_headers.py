"""
Simple script that simply grabs the headers of eachh packet from the radio

Header building code
void Telemetry::preparePacket(uint32_t timestamp) {
    this->packet[0] = 0;
    this->packet[1] = 0;
    this->packet[2] = 0;
    this->packet[3] = START_BYTE; // 51
    this->packet[4] = (timestamp >> 24) & 0xFF;
    this->packet[5] = (timestamp >> 16) & 0xFF;
    this->packet[6] = (timestamp >> 8) & 0xFF;
    this->packet[7] = timestamp & 0xFF;
    nextEmptyPacketIndex = 8;
}


Waits for a 0000 0033 (51) sequence, then reads the next 4 bytes as a timestamp
Each packet can be up to 120 bytes in length
"""

import struct
import time

import serial

if __name__ == "__main__":
    # Connect to /dev/ttyACM0 at 115200
    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    ser.flush()
    print("Connected to /dev/ttyACM0 at 115200 baud")
    start_time = time.time()
    while True:
        # Read until we find the start sequence
        byte = ser.read(1)
        if byte == b"\x00":
            byte2 = ser.read(1)
            if byte2 == b"\x00":
                byte3 = ser.read(1)
                if byte3 == b"\x00":
                    # Check for a 51
                    byte4 = ser.read(1)
                    if byte4 == b"\x33":
                        # We found the start sequence, read the next 4 bytes as timestamp
                        timestamp_bytes = ser.read(4)
                        if len(timestamp_bytes) < 4:
                            print("Incomplete timestamp bytes, exiting")
                            break
                        timestamp = struct.unpack(">I", timestamp_bytes)[0]
                        elapsed_ms = int((time.time() - start_time) * 1000)

                        # Next byte is an ID as int
                        id_byte = ser.read(1)
                        id = struct.unpack("B", id_byte)[0]

                        print(
                            f"Found packet with timestamp: {timestamp} ms after {elapsed_ms} ms and ID: {id}"
                        )

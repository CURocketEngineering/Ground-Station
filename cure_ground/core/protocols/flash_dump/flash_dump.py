"""
Flash dump protocol specification based on FlashCommands implementation
"""

import struct
from dataclasses import dataclass
from typing import List

COMMAND_CODE = b"\x03"
NULL_TERMINATOR = b"\x00"

# Response codes from FlashCommands.h
RESP_OK = 0x00
RESP_ERROR = 0xFF


@dataclass
class FlashDumpResponse:
    """Flash dump response data"""

    status: int
    data: bytes
    size: int


def create_flash_dump_command():
    """Create a flash dump command packet"""
    return b"<" + COMMAND_CODE + NULL_TERMINATOR + b">"


def parse_flash_dump_response(response: bytes) -> FlashDumpResponse:
    """
    Parse flash dump response

    Response format:
    - Status byte (0x00 for success)
    - Data length (4 bytes, little-endian)
    - Flash contents (variable length)
    """
    if len(response) < 5:
        raise ValueError("Response too short")

    status = response[0]
    if status != RESP_OK:
        raise ValueError(f"Error status received: {status}")

    # Extract data length (4 bytes, little-endian)
    data_length = struct.unpack("<I", response[1:5])[0]

    # Verify we have all the data
    if len(response) < 5 + data_length:
        raise ValueError(f"Incomplete data: expected {data_length} bytes, got {len(response)-5}")

    # Extract flash data
    flash_data = response[5 : 5 + data_length]

    return FlashDumpResponse(status=status, data=flash_data, size=data_length)


def parse_flash_data(data: bytes) -> List[dict]:
    """
    Parse flash memory contents into structured data
    Based on DataNames enum from dev_serial_flash_dump

    Data format:
    Repeated blocks of:
    - 1 byte: data type ID
    - 4 bytes: value (float or uint32 for timestamp)
    - 1 byte: newline character
    """
    DATA_BLOCK_SIZE = 6  # 1 byte type + 4 bytes value + 1 byte newline

    # Data type mapping from DataNames enum
    DATA_TYPES = {
        0: ("accelerometer_x", float),
        1: ("accelerometer_y", float),
        2: ("accelerometer_z", float),
        3: ("gyroscope_x", float),
        4: ("gyroscope_y", float),
        5: ("gyroscope_z", float),
        6: ("temperature", float),
        7: ("pressure", float),
        8: ("altitude", float),
        9: ("magnetometer_x", float),
        10: ("magnetometer_y", float),
        11: ("magnetometer_z", float),
        12: ("median_acceleration_squared", float),
        13: ("average_cycle_rate", float),
        14: ("timestamp", "uint32"),
    }

    structured_data = []
    current_record = {}

    for i in range(0, len(data), DATA_BLOCK_SIZE):
        block = data[i : i + DATA_BLOCK_SIZE]
        if len(block) != DATA_BLOCK_SIZE:
            break

        data_type = block[0]
        if data_type not in DATA_TYPES:
            continue

        name, value_type = DATA_TYPES[data_type]
        value_bytes = block[1:5]

        if value_type == float:
            value = struct.unpack("<f", value_bytes)[0]
        else:  # uint32
            value = struct.unpack("<I", value_bytes)[0]

        current_record[name] = value

        # If this was a timestamp, start a new record
        if name == "timestamp" and current_record:
            structured_data.append(current_record.copy())
            current_record = {}

    return structured_data

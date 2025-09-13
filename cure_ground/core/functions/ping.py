"""
Ping functionality implementation
"""

import time
from typing import Optional, Tuple

import serial

from ..protocols.immutable.ping import create_ping_command, parse_ping_response


def ping_device(
    port: str, baudrate: int = 115200, timeout: float = 1.0, retries: int = 3
) -> Tuple[bool, Optional[str]]:
    """
    Ping the MARTHA device

    Args:
        port: Serial port to use
        baudrate: Communication speed (default: 115200)
        timeout: Response timeout in seconds (default: 1.0)
        retries: Number of retry attempts (default: 3)

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            # Clear any pending data
            ser.reset_input_buffer()
            ser.reset_output_buffer()

            for attempt in range(retries):
                try:
                    # Send ping command
                    command = create_ping_command()
                    ser.write(command)

                    # Wait for response
                    start_time = time.time()
                    while ser.in_waiting < 4:  # Expected response size
                        if time.time() - start_time > timeout:
                            if attempt < retries - 1:
                                continue  # Try again
                            return False, "Response timeout"

                    # Read response
                    response = ser.read(4)
                    if parse_ping_response(response):
                        return True, None

                except serial.SerialException as e:
                    if attempt < retries - 1:
                        continue
                    return False, f"Serial communication error: {str(e)}"

            return False, "Maximum retries exceeded"

    except serial.SerialException as e:
        return False, f"Failed to open serial port: {str(e)}"

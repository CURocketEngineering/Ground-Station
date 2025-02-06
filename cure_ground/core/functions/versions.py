"""
Version information retrieval functionality
"""
import serial
import time
from typing import List, Optional, Tuple
from ..protocols.immutable.versions import (
    create_versions_command,
    parse_versions_response,
    VersionInfo
)

def get_versions(
    port: str,
    baudrate: int = 115200,
    timeout: float = 2.0,
    max_response_size: int = 1024
) -> Tuple[Optional[List[VersionInfo]], Optional[str]]:
    """
    Get version information from MARTHA device
    
    Args:
        port: Serial port to use
        baudrate: Communication speed (default: 115200)
        timeout: Response timeout in seconds (default: 2.0)
        max_response_size: Maximum response size in bytes (default: 1024)
        
    Returns:
        Tuple of (versions: Optional[List[VersionInfo]], error_message: Optional[str])
    """
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            # Clear any pending data
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Send versions command
            command = create_versions_command()
            ser.write(command)
            
            # Wait for initial response (at least 2 bytes - status and version count)
            start_time = time.time()
            while ser.in_waiting < 2:
                if time.time() - start_time > timeout:
                    return None, "Response timeout"
            
            # Read status and version count
            initial_response = ser.read(2)
            if len(initial_response) < 2:
                return None, "Incomplete response"
                
            version_count = initial_response[1]
            if version_count == 0:
                return [], None  # No versions reported
                
            # Wait for complete response
            # Each version has at least 4 bytes (2 lengths + minimum 1 char each)
            min_remaining = version_count * 4
            
            while ser.in_waiting < min_remaining:
                if time.time() - start_time > timeout:
                    return None, "Response timeout waiting for version data"
                    
            # Read the rest of the response
            remaining_data = ser.read(min(ser.in_waiting, max_response_size))
            
            try:
                # Combine initial response with remaining data
                full_response = initial_response + remaining_data
                versions = parse_versions_response(full_response)
                return versions, None
                
            except ValueError as e:
                return None, f"Failed to parse version data: {str(e)}"
                
    except serial.SerialException as e:
        return None, f"Serial communication error: {str(e)}"
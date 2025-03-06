"""
Versions protocol specification based on CoreCommands implementation
"""
from dataclasses import dataclass
from typing import List

COMMAND_CODE = b'\x02'
NULL_TERMINATOR = b'\x00'

# Response codes from CoreCommands.h
RESP_OK = 0x00
RESP_ERROR = 0xFF

@dataclass
class VersionInfo:
    """Version information for a system component"""
    component: str
    version: str

def create_versions_command():
    """Create a versions query command packet"""
    return b'<' + COMMAND_CODE + NULL_TERMINATOR + b'>'

def parse_versions_response(response: bytes) -> List[VersionInfo]:
    """
    Parse versions response into list of component versions
    
    Response format:
    - Status byte (0x00 for success)
    - Number of versions (1 byte)
    - For each version:
        - Component name length (1 byte)
        - Component name (variable)
        - Version string length (1 byte)
        - Version string (variable)
    """
    if len(response) < 3 or response[0] != RESP_OK:
        raise ValueError("Invalid response format or error status")
        
    versions = []
    num_versions = response[1]
    pos = 2  # Start after status and count
    
    for _ in range(num_versions):
        # Read component name
        name_len = response[pos]
        pos += 1
        component = response[pos:pos+name_len].decode('utf-8')
        pos += name_len
        
        # Read version string
        ver_len = response[pos]
        pos += 1
        version = response[pos:pos+ver_len].decode('utf-8')
        pos += ver_len
        
        versions.append(VersionInfo(component, version))
    
    return versions
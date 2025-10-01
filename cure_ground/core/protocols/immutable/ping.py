"""
Ping protocol specification based on CoreCommands implementation
"""

COMMAND_CODE = b"\x01"
NULL_TERMINATOR = b"\x00"

# Response codes from CoreCommands.h
RESP_OK = 0x00
RESP_ERROR = 0xFF


def create_ping_command():
    """Create a ping command packet"""
    return b"<" + COMMAND_CODE + NULL_TERMINATOR + b">"


def parse_ping_response(response):
    """
    Parse ping response
    Returns:
        bool: True if ping successful, False otherwise
    """
    if len(response) != 4:
        return False

    # Check packet format: <response_code>
    if response[0] != ord("<") or response[-1] != ord(">"):
        return False

    # Check command code and status
    return response[1] == ord(COMMAND_CODE) and response[2] == RESP_OK

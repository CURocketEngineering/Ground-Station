"""
Radio Data Source for CURE Ground Station
Parses radio telemetry data and provides it in a format compatible with StatusModel.

Location: cure_ground/data_sources/radio_data_source.py
"""

import struct
import time
from typing import Dict, List, Optional, Any
import serial

from cure_ground.core.protocols.data_names.data_name_loader import (
    load_data_name_enum,
    DataNames,
)
from cure_ground.core.protocols.states.states_loader import load_states, States
from cure_ground.data_sources import DataSource
from collections import deque


class RadioDataSource(DataSource):
    """Handles radio telemetry data reception and parsing."""

    START_SEQUENCE = [b"\x00", b"\x00", b"\x00", b"\x33"]
    END_SEQUENCE = [b"\x00", b"\x00", b"\x00", b"\x34"]

    def __init__(
        self,
        port: str,
        baudrate: int = 57600,
        timeout: int = 1,
        protocol_version: int = 3,
        states_version: int = 1,
    ):
        """
        Initialize the radio data source.

        Args:
            port: Serial port to connect to (e.g., "COM7" or "/dev/ttyUSB0")
            baudrate: Communication baud rate
            timeout: Serial read timeout in seconds
            protocol_version: Data names YAML version to load
            states_version: States YAML version to load
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self._connected = False

        # Load protocol definitions
        self.data_names: DataNames = load_data_name_enum(protocol_version)
        self.states: States = load_states(states_version)

        # Identify group IDs (multi-value packets) from data_names
        self.group_ids = set()
        self.group_component_mapping = {}  # Maps group ID to component IDs

        for item in self.data_names.data_definitions:
            if item.get("type") == "group":
                group_id = item["id"]
                self.group_ids.add(group_id)
                # Store the component IDs for this group
                if "data" in item:
                    self.group_component_mapping[group_id] = item["data"]

        # Store latest packet data for get_data()
        self.latest_data: Dict[str, str] = {}
        self.last_packet_time = 0

        # --- Rolling 100-packet retention tracking ---
        self._last_packet_number: Optional[int] = None
        self._packet_window = deque(maxlen=100)  # last 100 packet results
        self._packet_retention_ratio = 1.0
    
    
    def connect(self) -> bool:
        """
        Establish serial connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.ser.flush()
            self._connected = True
            print(f"RadioDataSource: Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException:
            # print(f"RadioDataSource: Failed to connect to {self.port}: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self._connected = False
        print("RadioDataSource: Disconnected from serial port")

    def is_connected(self) -> bool:
        """Check if data source is connected."""
        return self._connected and self.ser is not None and self.ser.is_open

    def get_data(self) -> Optional[Dict[str, Any]]:
        """
        Get latest data in StatusModel-compatible format.

        Returns:
            Dictionary mapping data names to string values, or None if no data
        """
        if not self.is_connected():
            return None

        # Try to read a new packet
        packet = self._read_packet()
        if packet:
            self._update_latest_data(packet)

        # Return the latest data we have (even if packet read failed)
        return self.latest_data if self.latest_data else None

    def _update_latest_data(self, packet: Dict):
        """
        Convert raw packet data to StatusModel format.
        Updates self.latest_data with new values.

        Args:
            packet: Raw packet from _read_packet()
        """
        # Update timestamp (convert from ms to seconds)
        timestamp_sec = packet["timestamp"] / 1000.0
        self.latest_data["TIMESTAMP"] = f"{timestamp_sec:.3f}"
        self.last_packet_time = time.time()

        # Process each data entry in the packet
        for entry in packet["data"]:
            data_id = entry["id"]

            try:
                info = self.data_names.get_info_by_id(data_id)
                name = info["name"]

                if data_id in self.group_ids:
                    # Group type - unpack into individual components
                    component_ids = self.group_component_mapping.get(data_id, [])
                    values = entry["values"]

                    for i, (comp_id, value) in enumerate(zip(component_ids, values)):
                        try:
                            comp_info = self.data_names.get_info_by_id(comp_id)
                            comp_name = comp_info["name"]
                            self.latest_data[comp_name] = value
                        except (KeyError, IndexError):
                            pass
                else:
                    self.latest_data[name] = entry["float_value"]

            except KeyError:
                # Unknown ID - skip it
                pass

    def _read_until_start_sequence(self) -> bool:
        """
        Read bytes until start sequence is found.

        Returns:
            True if start sequence found, False on timeout
        """
        buffer = []
        while True:
            byte = self.ser.read(1)
            if not byte:  # Timeout
                return False
            buffer.append(byte)
            if len(buffer) >= 4 and buffer[-4:] == self.START_SEQUENCE:
                return True

    def _read_timestamp(self) -> int:
        """
        Read and parse 4-byte timestamp.

        Returns:
            Timestamp value in milliseconds
        """
        timestamp_bytes = self.ser.read(4)
        if len(timestamp_bytes) != 4:
            raise IOError("Failed to read timestamp")
        return struct.unpack(">I", timestamp_bytes)[0]

    def _read_packet_number(self) -> int:
        """
        Read and parse 4-byte packet number.

        Returns:
            Packet number as integer
        """
        packet_num_bytes = self.ser.read(4)
        if len(packet_num_bytes) != 4:
            raise IOError("Failed to read packet number")
        return struct.unpack(">I", packet_num_bytes)[0]

    def _parse_data_entry(self, data_id: int, data_bytes: bytes) -> Dict:
        """
        Parse a single data entry.

        Args:
            data_id: The sensor/data ID
            data_bytes: Raw data bytes

        Returns:
            Dictionary with parsed data
        """
        result = {"id": data_id}

        if data_id in self.group_ids:
            # Group type: 12 bytes = 3 floats (little-endian)
            float_values = []
            for i in range(3):
                byte_data = bytes(
                    [
                        data_bytes[i * 4 + 3],
                        data_bytes[i * 4 + 2],
                        data_bytes[i * 4 + 1],
                        data_bytes[i * 4],
                    ]
                )
                float_value = struct.unpack("<f", byte_data)[0]
                float_values.append(float_value)
            result["values"] = float_values
        else:
            # Single value: 4 bytes (big-endian)
            float_value = struct.unpack(">f", data_bytes)[0]
            result["float_value"] = float_value

        return result

    def _read_packet_data(self) -> List[Dict]:
        """
        Read all data entries in a packet until end sequence.

        Returns:
            List of parsed data dictionaries
        """
        packet_data = []
        assert self.ser is not None, "Serial connection not established"

        while True:
            # Read ID byte
            buffer = []
            id_byte = self.ser.read(1)
            if not id_byte:
                break

            buffer.append(id_byte)
            data_id = struct.unpack("B", id_byte)[0]

            # Read first 3 bytes of data
            data_bytes = bytes()
            for _ in range(3):
                next_byte = self.ser.read(1)
                if not next_byte:
                    return packet_data
                data_bytes += next_byte
                buffer.append(next_byte)

            # Check if we hit end sequence
            if buffer == self.END_SEQUENCE:
                break

            # Determine expected data length based on whether ID is a group
            expected_length = 12 if data_id in self.group_ids else 4

            # Read remaining data bytes
            while len(data_bytes) < expected_length:
                data_byte = self.ser.read(1)
                if not data_byte:
                    return packet_data
                data_bytes += data_byte

            # Parse and store the data
            try:
                parsed_data = self._parse_data_entry(data_id, data_bytes)
                packet_data.append(parsed_data)
            except Exception as e:
                print(f"RadioDataSource: Error parsing data ID {data_id}: {e}")
                continue

        return packet_data

    def _read_packet(self) -> Optional[Dict]:
        """
        Read a complete radio packet.

        Returns:
            Dictionary containing timestamp and parsed data, or None if no packet
        """
        if not self.is_connected():
            return None

        try:
            # Find start sequence
            if not self._read_until_start_sequence():
                return None

            # Read timestamp
            timestamp = self._read_timestamp()

            # Read packet number
            packet_number = self._read_packet_number()
            self._update_packet_retention(packet_number)

            # Read all data in packet
            packet_data = self._read_packet_data()

            return {
                "timestamp": timestamp,
                "packet_number": packet_number,
                "data": packet_data,
                "receive_time": time.time(),
            }

        except Exception as e:
            print(f"RadioDataSource: Error reading packet: {e}")
            return None
        
    def _update_packet_retention(self, packet_number: int):
        """
        Rolling 100-packet retention window.
        1 = packet received
        0 = packet lost
        Updates for every packet recevied, and then looks
        at the past 100 packets read in
        The percentage of received packets is calculated
        """

        if self._last_packet_number is None:
            self._last_packet_number = packet_number
            self._packet_window.append(1)
            return

        diff = packet_number - self._last_packet_number

        if diff > 1:
            # Missed packets → add zeros
            for _ in range(diff - 1):
                self._packet_window.append(0)

        # Current packet received
        self._packet_window.append(1)

        self._last_packet_number = packet_number

        # Only calculate once window fills
        if len(self._packet_window) == self._packet_window.maxlen:
            self._packet_retention_ratio = (
                sum(self._packet_window) / self._packet_window.maxlen
            )
        else:
            # Until full, show 100%
            self._packet_retention_ratio = 1.0

    def get_packet_retention_ratio(self) -> float:
        return self._packet_retention_ratio

    def get_available_ports(self) -> List[str]:
        """
        Get list of available serial ports.

        Returns:
            List of port names
        """
        import serial.tools.list_ports

        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

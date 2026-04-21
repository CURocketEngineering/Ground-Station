"""
Radio Data Source for CURE Ground Station
Parses radio telemetry data and provides it in a format compatible with StatusModel.

Location: cure_ground/data_sources/radio_data_source.py
"""

import struct
import time
from typing import Dict, List, Optional, Any
import serial
from collections import deque

from cure_ground.core.protocols.data_names.data_name_loader import (
    load_data_name_enum,
    DataNames,
)
from cure_ground.core.protocols.states.states_loader import load_states, States
from cure_ground.data_sources import DataSource


class RadioDataSource(DataSource):
    """Handles radio telemetry data reception and parsing."""

    START_SEQUENCE = b"\x00\x00\x00\x33"
    END_SEQUENCE = b"\x00\x00\x00\x34"
    MAX_RX_BUFFER_BYTES = 65536
    RECONNECT_INTERVAL_SECONDS = 1.0
    STALE_LINK_TIMEOUT_SECONDS = 5.0

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
        self._desired_connection = False
        self._last_connect_attempt_monotonic = 0.0
        self._last_radio_activity_monotonic = 0.0
        self._received_data_since_connect = False

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

        # Rolling serial RX buffer for chunked / delayed packet arrival.
        self._rx_buffer = bytearray()

    def connect(self, port: Optional[str] = None) -> bool:
        """
        Establish serial connection.

        Returns:
            True if connection successful, False otherwise
        """
        if port is not None:
            self.port = port

        self._desired_connection = True
        self._last_connect_attempt_monotonic = time.monotonic()
        return self._open_serial_port()

    def _open_serial_port(self) -> bool:
        self._close_serial_port()

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.ser.flush()
            self.ser.reset_input_buffer()
            self._reset_runtime_state()
            self._rx_buffer.clear()
            self._connected = True
            print(f"RadioDataSource: Connected to {self.port} at {self.baudrate} baud")
            return True
        except (serial.SerialException, OSError) as exc:
            self._connected = False
            self.ser = None
            print(f"RadioDataSource: Failed to connect to {self.port}: {exc}")
            return False

    def disconnect(self):
        """Close serial connection."""
        self._desired_connection = False
        self._close_serial_port()
        self._reset_runtime_state()
        self.latest_data = {}
        self.last_packet_time = 0
        print("RadioDataSource: Disconnected from serial port")

    def _close_serial_port(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except (serial.SerialException, OSError):
                pass
        self.ser = None
        self._rx_buffer.clear()
        self._connected = False

    def _reset_runtime_state(self):
        self._last_packet_number = None
        self._packet_window.clear()
        self._packet_retention_ratio = 1.0
        self._last_radio_activity_monotonic = time.monotonic()
        self._received_data_since_connect = False

    def _mark_connection_lost(self, reason: str):
        if self._connected:
            print(f"RadioDataSource: Connection lost ({reason}); will retry")
        self._close_serial_port()

    def _maybe_reconnect(self) -> bool:
        if not self._desired_connection:
            return False

        if self.ser is not None and self.ser.is_open:
            return True

        now = time.monotonic()
        if now - self._last_connect_attempt_monotonic < self.RECONNECT_INTERVAL_SECONDS:
            return False

        self._last_connect_attempt_monotonic = now
        return self._open_serial_port()

    def _connection_is_stale(self) -> bool:
        if not self._connected or not self._received_data_since_connect:
            return False

        return (
            time.monotonic() - self._last_radio_activity_monotonic
            >= self.STALE_LINK_TIMEOUT_SECONDS
        )

    def is_connected(self) -> bool:
        """Check if data source is connected."""
        if self._connection_is_stale():
            self._mark_connection_lost("no radio data received")
            return self._maybe_reconnect()

        if self._connected and self.ser is not None and self.ser.is_open:
            return True

        return self._maybe_reconnect()

    def get_data(self) -> Optional[Dict[str, Any]]:
        """
        Get latest data in StatusModel-compatible format.

        Returns:
            Dictionary mapping data names to string values, or None if no data
        """
        if not self.is_connected():
            return None

        self._ingest_available_bytes()

        # Process all complete packets currently in the buffer.
        while True:
            packet = self._read_packet()
            if not packet:
                break
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
        timestamp_ms = packet["timestamp"]
        self.latest_data["TIMESTAMP"] = f"{timestamp_ms}"
        self.latest_data["NUM_PACKETS_SENT"] = str(int(packet["packet_number"]))
        self.last_packet_time = int(time.time() * 1000)

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

    def _ingest_available_bytes(self):
        """
        Pull all currently available serial bytes into the RX buffer.
        """
        assert self.ser is not None, "Serial connection not established"

        try:
            available = self.ser.in_waiting
        except (serial.SerialException, OSError) as exc:
            self._mark_connection_lost(f"failed to check bytes waiting: {exc}")
            return

        if available <= 0:
            return

        try:
            new_bytes = self.ser.read(available)
        except (serial.SerialException, OSError) as exc:
            self._mark_connection_lost(f"failed while reading serial bytes: {exc}")
            return

        if not new_bytes:
            return

        self._rx_buffer.extend(new_bytes)
        self._last_radio_activity_monotonic = time.monotonic()
        self._received_data_since_connect = True

        # Guard against unbounded growth while preserving best-effort sync data.
        if len(self._rx_buffer) > self.MAX_RX_BUFFER_BYTES:
            start_idx = self._rx_buffer.rfind(self.START_SEQUENCE)
            if start_idx > 0:
                del self._rx_buffer[:start_idx]

            if len(self._rx_buffer) > self.MAX_RX_BUFFER_BYTES:
                del self._rx_buffer[: -self.MAX_RX_BUFFER_BYTES]

    def _align_buffer_to_start_sequence(self) -> bool:
        """
        Align buffer start to the start sequence.

        Returns:
            True if start sequence is present at buffer index 0.
        """
        start_idx = self._rx_buffer.find(self.START_SEQUENCE)
        if start_idx == -1:
            # Keep only a short suffix so split start markers can still match later.
            keep_tail = len(self.START_SEQUENCE) - 1
            if len(self._rx_buffer) > keep_tail:
                del self._rx_buffer[:-keep_tail]
            return False

        if start_idx > 0:
            del self._rx_buffer[:start_idx]

        return True

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

    def _extract_next_packet_from_buffer(self) -> Optional[Dict]:
        """
        Parse one complete packet from RX buffer if available.

        Returns:
            Parsed packet dict when complete packet is present, else None.
        """
        if not self._align_buffer_to_start_sequence():
            return None

        # start(4) + timestamp(4) + packet_number(4)
        if len(self._rx_buffer) < 12:
            return None

        try:
            timestamp = struct.unpack(">I", bytes(self._rx_buffer[4:8]))[0]
            packet_number = struct.unpack(">I", bytes(self._rx_buffer[8:12]))[0]
        except struct.error as e:
            print(f"RadioDataSource: Error parsing packet header: {e}")
            del self._rx_buffer[:1]
            return None

        cursor = 12
        packet_data: List[Dict] = []

        while True:
            remaining = len(self._rx_buffer) - cursor
            if remaining < 4:
                return None

            if bytes(self._rx_buffer[cursor : cursor + 4]) == self.END_SEQUENCE:
                packet_end = cursor + 4
                del self._rx_buffer[:packet_end]
                self._update_packet_retention(packet_number)
                self._last_radio_activity_monotonic = time.monotonic()
                self._received_data_since_connect = True
                return {
                    "timestamp": timestamp,
                    "packet_number": packet_number,
                    "data": packet_data,
                    "receive_time": int(time.time() * 1000),
                }

            data_id = self._rx_buffer[cursor]
            expected_length = 12 if data_id in self.group_ids else 4
            entry_total = 1 + expected_length

            if remaining < entry_total:
                return None

            data_bytes = bytes(
                self._rx_buffer[cursor + 1 : cursor + 1 + expected_length]
            )

            try:
                parsed_data = self._parse_data_entry(data_id, data_bytes)
                packet_data.append(parsed_data)
            except Exception as e:
                print(f"RadioDataSource: Error parsing data ID {data_id}: {e}")
                # Drop one byte and resync on next iteration.
                del self._rx_buffer[:1]
                return None

            cursor += entry_total

    def _read_packet(self) -> Optional[Dict]:
        """
        Read a complete radio packet.

        Returns:
            Dictionary containing timestamp and parsed data, or None if no packet
        """
        if not self.is_connected():
            return None

        try:
            return self._extract_next_packet_from_buffer()
        except Exception as e:
            print(f"RadioDataSource: Error reading packet: {e}")
            return None

    def send_command(self, command: str, add_newline: bool = True) -> bool:
        if not self.is_connected() or self.ser is None:
            return False

        try:
            payload = command + ("\n" if add_newline else "")
            self.ser.write(payload.encode("utf-8"))
            self.ser.flush()
            return True
        except (serial.SerialException, OSError) as exc:
            self._mark_connection_lost(f"failed to send command '{command}': {exc}")
            return False

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

import time
import struct
from typing import Dict, Optional
from .SerialDataSource import SerialDataSource

class RadioDataSource(SerialDataSource):
    def __init__(self, baudrate=57600):
        super().__init__(baudrate=baudrate)
        self.buffer = bytearray()
        
        # Data packet definitions from PDF
        self.PACKET_START = {
            0x52: self._parse_2hz_packet,  # 2Hz data
            0x51: self._parse_1hz_packet   # 1Hz data
        }
        
        # Data type mappings
        self.DATA_TYPES = {
            102: 'ACCL',  # Accelerometer
            105: 'GYRO',  # Gyroscope
            8: 'ALT',     # Altitude
            19: 'EST_ALTITUDE',  # Estimated altitude
            6: 'TEMP',    # Temperature
            7: 'PRESSURE', # Pressure
            111: 'MAG',   # Magnetometer
            13: 'CYCLE_RATE', # Cycle rate
            15: 'STATE',  # State
            20: 'BATT',   # Battery
            16: 'FLIGHT_ID' # Flight ID
        }
        
        # State mappings
        self.STATES = {
            0: 'UNARMED',
            1: 'ARMED', 
            2: 'ASCENT',
            3: 'POWERED_ASCENT',
            4: 'COAST_ASCENT',
            5: 'DESCENT',
            6: 'DROGUE_DEPLOYED',
            7: 'MAIN_DEPLOYED',
            8: 'LANDED'
        }
    
    def connect(self, port: str = None) -> bool:
        # Connect to radio via serial port
        if port is None:
            ports = self.get_available_ports()
            for port in ports:
                if port != "No Ports Available":
                    if super().connect(port):
                        self.buffer = bytearray()
                        print(f"Connected to radio on {port}")
                        return True
            return False
        else:
            result = super().connect(port)
            if result:
                self.buffer = bytearray()
            return result
    
    def disconnect(self) -> None:
        # Disconnect from radio
        super().disconnect()
        self.buffer = bytearray()
    
    def get_data(self) -> Optional[Dict[str, str]]:
        # Get the next data packet from radio
        if not self.is_connected():
            return None
            
        # Read available data
        if self.ser and self.ser.in_waiting:
            new_data = self.ser.read(self.ser.in_waiting)
            self.buffer.extend(new_data)
            
            # Process complete packets from buffer
            return self._process_buffer()
        return None
    
    def _process_buffer(self) -> Optional[Dict[str, str]]:
        # Process buffer to find complete packets
        data_dict = {}
        
        while len(self.buffer) >= 2:  # Need at least start byte + some data
            start_byte = self.buffer[0]
            
            if start_byte in self.PACKET_START:
                # Try to parse packet
                parser = self.PACKET_START[start_byte]
                result = parser(self.buffer)
                
                if result:
                    data_dict.update(result['data'])
                    # Remove processed bytes from buffer
                    self.buffer = self.buffer[result['bytes_processed']:]
                    
                    # Return the collected data
                    if data_dict:
                        return data_dict
                else:
                    # Incomplete packet, wait for more data
                    break
            else:
                # Invalid start byte, skip it
                self.buffer.pop(0)
        
        return None if not data_dict else data_dict
    
    def _parse_2hz_packet(self, buffer: bytearray) -> Optional[Dict]:
        # Parse 2Hz data packet (start byte 0x52)
        # Minimum packet: start(1) + timestamp(4) + at least one data group
        if len(buffer) < 6:
            return None
            
        data = {}
        bytes_processed = 1  # Start byte
        
        try:
            # Parse timestamp (4 bytes, int32)
            if len(buffer) < bytes_processed + 4:
                return None
                
            timestamp = struct.unpack('<i', buffer[bytes_processed:bytes_processed+4])[0]
            data['TIMESTAMP'] = str(timestamp)
            bytes_processed += 4
            
            # Parse data groups until end of buffer
            while bytes_processed < len(buffer):
                data_type = buffer[bytes_processed]
                bytes_processed += 1
                
                if data_type in [102, 105, 111]:  # ACCL, GYRO, MAG - 3 floats
                    if len(buffer) < bytes_processed + 12:
                        return None
                    
                    x, y, z = struct.unpack('<fff', buffer[bytes_processed:bytes_processed+12])
                    prefix = self.DATA_TYPES.get(data_type, f'UNKNOWN_{data_type}')
                    data[f'{prefix}_X'] = f"{x:.2f}"
                    data[f'{prefix}_Y'] = f"{y:.2f}" 
                    data[f'{prefix}_Z'] = f"{z:.2f}"
                    bytes_processed += 12
                    
                elif data_type in [8, 19]:  # ALT, EST_ALTITUDE - 2 bytes int16
                    if len(buffer) < bytes_processed + 2:
                        return None
                    
                    alt = struct.unpack('<h', buffer[bytes_processed:bytes_processed+2])[0]
                    prefix = self.DATA_TYPES.get(data_type, f'UNKNOWN_{data_type}')
                    data[prefix] = str(alt)
                    bytes_processed += 2
                    
                elif data_type in [6, 7, 13, 15, 16]:  # TEMP, PRESSURE, CYCLE_RATE, STATE, FLIGHT_ID - 1 byte int
                    if len(buffer) < bytes_processed + 1:
                        return None
                    
                    value = buffer[bytes_processed]
                    prefix = self.DATA_TYPES.get(data_type, f'UNKNOWN_{data_type}')
                    
                    if data_type == 15:  # STATE - convert to state name
                        data[prefix] = self.STATES.get(value, f'UNKNOWN_STATE_{value}')
                    else:
                        data[prefix] = str(value)
                    bytes_processed += 1
                    
                elif data_type == 20:  # BATT - 1 byte float8
                    if len(buffer) < bytes_processed + 1:
                        return None
                    
                    voltage = buffer[bytes_processed] / 10.0  # Assuming 0.1V resolution
                    data['BATT'] = f"{voltage:.1f}"
                    bytes_processed += 1
                    
                else:
                    # Unknown data type, stop parsing this packet
                    break
            
            return {'data': data, 'bytes_processed': bytes_processed}
            
        except (struct.error, IndexError):
            return None
    
    def _parse_1hz_packet(self, buffer: bytearray) -> Optional[Dict]:
        # Parse 1Hz data packet (start byte 0x51)
        # This follows similar structure to 2Hz but different data frequency
        # For now, use the same parser since data format is the same
        return self._parse_2hz_packet(buffer)
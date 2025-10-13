import serial
import serial.tools.list_ports
import time
from typing import List, Optional, Dict
from .DataSource import DataSource

class SerialDataSource(DataSource):
    def __init__(self, baudrate: int = 115200, timeout: float = 1.0):
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.connected = False
        
    def get_available_ports(self) -> List[str]:
        # Get list of available serial ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports] if ports else ["No Ports Available"]
    
    def connect(self, port: str = None) -> bool:
        # Establish serial connection
        if port is None:
            ports = self.get_available_ports()
            if not ports or ports[0] == "No Ports Available":
                return False
            port = ports[0]
            
        try:
            self.ser = serial.Serial(port, self.baudrate, timeout=self.timeout)
            self.connected = True
            # Clear buffer on connect
            time.sleep(0.1)
            self.ser.reset_input_buffer()
            return True
        except Exception as e:
            print(f"Error opening serial port {port}: {e}")
            self.connected = False
            return False
            
    def disconnect(self) -> None:
        # Close serial connection
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
            
    def send_command(self, command: str, add_newline: bool = True) -> bool:
        # Send command to device
        if not self.connected or not self.ser or not self.ser.is_open:
            return False
            
        try:
            cmd = command + '\n' if add_newline else command
            self.ser.write(cmd.encode('utf-8'))
            self.ser.flush()  # Ensure data is sent
            return True
        except Exception as e:
            print(f"Error sending command '{command}': {e}")
            self.connected = False
            return False
            
    def read_response(self, timeout: float = 0.2) -> str:
        # Read response from device
        if not self.connected or not self.ser or not self.ser.is_open:
            return ""
            
        time.sleep(timeout)
        if self.ser.in_waiting:
            try:
                return self.ser.read(self.ser.in_waiting).decode('utf-8')
            except UnicodeDecodeError:
                return "Error decoding response"
        return ""
    
    def get_data(self) -> Optional[Dict[str, str]]:
        # Get data from serial - for direct serial communication
        # This would be overridden for specific protocols
        # For generic serial, you might want to read raw data
        response = self.read_response()
        if response:
            return {'raw_data': response}
        return None
    
    def is_connected(self) -> bool:
        # Check if connection is active
        return self.connected and self.ser and self.ser.is_open
    
    def clear_buffer(self):
        # Clear the serial input buffer
        if self.is_connected():
            self.ser.reset_input_buffer()
import serial
import serial.tools.list_ports
import time
from typing import List, Optional, Tuple

class SerialConnection:
    def __init__(self):
        self.ser = None
        self.connected = False
        
    def get_available_ports(self) -> List[str]:
        """Get list of available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports] if ports else ["No Ports Available"]
    
    def connect(self, port: str, baudrate: int = 115200, timeout: float = 1.0) -> bool:
        """Establish serial connection"""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            self.connected = True
            # Clear buffer on connect
            time.sleep(0.1)
            self.ser.reset_input_buffer()
            return True
        except Exception as e:
            print(f"Error opening serial port {port}: {e}")
            self.connected = False
            return False
            
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
            
    def send_command(self, command: str, add_newline: bool = True) -> bool:
        """Send command to device"""
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
        """Read response from device"""
        if not self.connected or not self.ser or not self.ser.is_open:
            return ""
            
        time.sleep(timeout)
        if self.ser.in_waiting:
            try:
                return self.ser.read(self.ser.in_waiting).decode('utf-8')
            except UnicodeDecodeError:
                return "Error decoding response"
        return ""
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self.connected and self.ser and self.ser.is_open
    
    def clear_buffer(self):
        """Clear the serial input buffer"""
        if self.is_connected():
            self.ser.reset_input_buffer()
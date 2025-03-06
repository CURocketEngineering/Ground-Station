"""
Flash memory dump functionality
"""
import serial
import time
import pandas as pd
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path
from tqdm import tqdm
from ..protocols.flash_dump.flash_dump import (
    create_flash_dump_command,
    parse_flash_dump_response,
    parse_flash_data
)

def dump_flash(
    port: str,
    output_file: str,
    baudrate: int = 115200,
    timeout: float = 10.0,
    chunk_size: int = 4096
) -> Tuple[bool, Optional[str]]:
    """
    Dump flash memory contents to a CSV file
    
    Args:
        port: Serial port to use
        output_file: Path to save the CSV file
        baudrate: Communication speed (default: 115200)
        timeout: Response timeout in seconds (default: 10.0)
        chunk_size: Size of chunks to read at a time (default: 4096)
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            # Clear any pending data
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Send flash dump command
            command = create_flash_dump_command()
            ser.write(command)
            
            # Wait for initial response (at least 5 bytes - status and size)
            start_time = time.time()
            while ser.in_waiting < 5:
                if time.time() - start_time > timeout:
                    return False, "Response timeout"
            
            # Read status and size
            header = ser.read(5)
            if len(header) < 5:
                return False, "Incomplete response header"
                
            try:
                # Parse initial response to get total size
                initial_response = parse_flash_dump_response(header)
                total_size = initial_response.size
                
                # Read data in chunks with progress bar
                data = bytearray()
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    while len(data) < total_size:
                        if time.time() - start_time > timeout:
                            return False, "Response timeout during data transfer"
                            
                        if ser.in_waiting > 0:
                            chunk = ser.read(min(chunk_size, ser.in_waiting))
                            data.extend(chunk)
                            pbar.update(len(chunk))
                
                # Parse the flash data into structured format
                structured_data = parse_flash_data(data)
                
                # Convert to DataFrame and save
                df = pd.DataFrame(structured_data)
                
                # Ensure output directory exists
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save to CSV
                df.to_csv(output_file, index=False)
                return True, None
                
            except ValueError as e:
                return False, f"Failed to parse flash data: {str(e)}"
                
    except serial.SerialException as e:
        return False, f"Serial communication error: {str(e)}"

def generate_graphs(csv_path: str) -> Tuple[bool, Optional[str]]:
    """
    Generate graphs from flash dump CSV data
    Based on dev_serial_flash_dump/gen_graphs.py
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        import matplotlib.pyplot as plt
        
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Create output directory
        save_path = Path(csv_path).with_suffix('')/'graphs'
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Generate individual graphs
        for col in df.columns:
            if col == 'timestamp':
                continue
                
            # Interpolate missing values
            df[col] = df[col].interpolate(method='linear', limit_direction='both')
            
            plt.figure()
            plt.plot(df['timestamp'], df[col])
            plt.title(col)
            plt.xlabel('Timestamp')
            plt.ylabel(col)
            plt.savefig(save_path/f'{col}.png')
            plt.close()
            
        # Generate combined accelerometer graph
        plt.figure()
        plt.plot(df['timestamp'], df['accelerometer_x'], label='accelerometer_x')
        plt.plot(df['timestamp'], df['accelerometer_y'], label='accelerometer_y')
        plt.plot(df['timestamp'], df['accelerometer_z'], label='accelerometer_z')
        plt.title('Accelerometer Data')
        plt.xlabel('Timestamp')
        plt.ylabel('m/s^2')
        plt.legend()
        plt.savefig(save_path/'accelerometer.png')
        plt.close()
        
        return True, None
        
    except Exception as e:
        return False, f"Failed to generate graphs: {str(e)}"
# serial_handler.py
"""Module for handling serial communication."""
import serial
import serial.tools.list_ports as list_ports
from config import BAUDRATE, TIMEOUT

class SerialHandler:
    def __init__(self):
        self.port = None
        
    def initialize_port(self):
        """Initialize serial port with user selection."""
        ports = list_ports.comports()
        port_list = [port.name for port in ports]
        print(f"Available ports: {port_list}")
        
        if len(ports)<1:
            while True:
                print(f"Ports available: {port_list}")
                try:
                    choice = int(input(f"elegi un puerto (index de 0 a n):"))
                    if choice < len(port_list):
                        self.port = serial.Serial(
                            port=port_list[choice],
                            baudrate=BAUDRATE,
                            timeout=TIMEOUT
                        )
                        self.port.flushInput()
                        self.port.flushOutput()
                        return True
                except (ValueError, IndexError):
                    print("Invalid selection. Try again.")
        elif len(ports) == 1:
            self.port = serial.Serial(
                port=port_list[0],
                baudrate=BAUDRATE,
                timeout=TIMEOUT
            )
        else: print("No serial ports available.")
        return False
        
    def read_data(self):
        """Read and parse data from serial port."""
        if self.port:
            try:
                self.port.flush()
                data = self.port.readline()
                return float(data.decode('utf-8').strip().strip('\x00').split('|')[0])
            except Exception as e:
                print(f"Error reading data: {e}")
        return None
        
    def write_data(self, value):
        """Write value to serial port."""
        if self.port:
            try:
                self.port.write(str(value).encode())
            except Exception as e:
                print(f"Error writing data: {e}")

if __name__ == "__main__":
    handler = SerialHandler()
    handler.initialize_port()
    print(handler.read_data())
    while True:
        print(handler.read_data())
        handler.write_data(1.0)
# serial_handler.py
"""Module for handling serial communication."""
import serial
import serial.tools.list_ports as list_ports
from config import BAUDRATE, TIMEOUT

class SerialHandler:
    """SerialHandler class for handling serial port communication.
    Methods:
        __init__:
            Initializes the SerialHandler instance with default values.
        initialize_port:
            Initializes the serial port based on user selection or available ports.
            Returns True if the port is successfully initialized, otherwise False.
        read_data:
            Reads and parses data from the serial port.
            Returns a list of float values if data is successfully read, otherwise None.
        write_data:
            Writes a given value to the serial port.
    """
    def __init__(self):
        self.port = None
        
    def initialize_port(self):
        """Initialize serial port with user selection."""
        import sys
        all_ports = list_ports.comports()
        # On Windows show only COM*, on Linux only /dev/ttyACM*
        if sys.platform.startswith("win"):
            ports = [p for p in all_ports if p.device.upper().startswith("COM")]
        else:
            ports = [p for p in all_ports if p.device.startswith("/dev/ttyACM")]
        if not ports:
            print("No matching serial ports found.")
            return False

        print("Available ports:")
        for idx, p in enumerate(ports):
            print(f"  {idx}: {p.device} — {p.description}")

        if len(ports) > 1:
            # multiple → user picks
            while True:
                choice = input(f"Select a port index (0–{len(ports)-1}): ")
                try:
                    i = int(choice)
                    if 0 <= i < len(ports):
                        sel = ports[i].device
                        self.port = serial.Serial(sel, baudrate=BAUDRATE, timeout=TIMEOUT)
                        self.port.reset_input_buffer()
                        return True
                except:
                    pass
                print("Invalid selection, try again.")
        else:
            # exactly one → auto open
            sel = ports[0].device
            self.port = serial.Serial(sel, baudrate=BAUDRATE, timeout=TIMEOUT)
            self.port.reset_input_buffer()
            return True

        return False
        
    def read_data(self):
        """Read and parse data from serial port. and return list with the read items
        Returns: list of float values
        """
        if self.port:
            try:
                self.port.flush()
                data = self.port.readline()
                if data:
                    return [float(x) for x in data.decode('utf-8').strip().strip('\x00').split('|')]
                return float([0])
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
import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import numpy as np
import serial
import serial.tools.list_ports as list_ports
import matplotlib.style as plot_style

# Configure Matplotlib
matplotlib.use('TkAgg')
try:
    plot_style.use(['science', 'dark_background'])
except Exception:
    plot_style.use('dark_background')


class SerialPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plot Example")
        self.root.geometry("800x450")
        self.style = Style(theme='darkly')

        # Initialize serial port
        self.serial_port = None
        self.initialize_serial_port()

        # Initialize plot
        self.fig, self.ax = self.create_plot()
        self.x_data = [0]
        self.y_data = [0]

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Controls
        self.reference_value = tk.DoubleVar(value=1.0)
        self.create_controls()

        # Animation
        self.ani = animation.FuncAnimation(self.fig, self.update_plots, interval=100, blit=True)

    def initialize_serial_port(self):
        """Initialize and configure the serial port."""
        ports = list_ports.comports()
        port_list = [port.name for port in ports]
        if len(ports)-1:
            while True:
                print(f"Available ports: {port_list}")
                try:
                    choice = int(input("Select a port index (0 to n): "))
                    if 0 <= choice < len(port_list):
                        self.serial_port = serial.Serial(port=port_list[choice], baudrate=9600, timeout=2)
                        self.serial_port.flushInput()
                        self.serial_port.flushOutput()
                        print(f"Connected to {port_list[choice]}")
                        break
                except (ValueError, IndexError):
                    print("Invalid selection. Try again.")
        else:
            print("No serial ports available.")
            self.serial_port = None

    def create_plot(self):
        """Create and configure the Matplotlib figure and axes."""
        fig = Figure(figsize=(5, 3), facecolor='#333333')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#333333')
        ax.set_ylim([-10, 110])
        self.line1, = ax.plot([], [], color='#ff9900', label='Signal')
        self.line2, = ax.plot([], [], color='#ff2900', label='Ref')
        ax.legend(loc='upper left')
        return fig, ax

    def create_controls(self):
        """Create the control panel with sliders and buttons."""
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        ttk.Label(controls_frame, text="Reference:").grid(row=0, column=0, padx=5, pady=5)
        reference_entry = ttk.Entry(controls_frame, textvariable=self.reference_value)
        reference_entry.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        reference_slider = ttk.Scale(
            controls_frame, from_=0.0, to=5.0, orient=tk.HORIZONTAL,
            variable=self.reference_value, command=lambda _: self.update_plots(None)
        )
        reference_slider.grid(row=2, column=0, padx=5, pady=5, sticky='ew')

        ttk.Button(
            controls_frame, text="Connect", command=self.initialize_serial_port,
            style='primary.Outline.TButton'
        ).grid(row=0, column=1, padx=5, pady=10)

        ttk.Button(
            controls_frame, text="Export", command=lambda: self.update_plots(None),
            style='primary.Outline.TButton'
        ).grid(row=0, column=2, padx=5, pady=10)

    def update_plots(self, frame):
        """Update the plot with new data."""
        if self.serial_port:
            try:
                self.serial_port.flush()
                reference_value = self.reference_value.get()
                self.serial_port.write(str(reference_value).encode())
                data = self.serial_port.readline().decode('utf-8').strip()
                new_y = float(data)

                new_x = self.x_data[-1] + 0.1
                self.x_data.append(new_x)
                self.y_data.append(new_y)

                # Update plot data
                self.line1.set_data(self.x_data, self.y_data)
                self.line2.set_ydata([reference_value, reference_value])
                self.ax.set_xlim(new_x - 15, new_x + 0.5)

                return self.line1, self.line2
            except Exception as e:
                print(f"Error reading serial data: {e}")
        return self.line1, self.line2


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialPlotApp(root)
    root.mainloop()

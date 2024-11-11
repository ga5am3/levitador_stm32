import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import numpy as np
import serial
import serial.tools.list_ports as list_ports
import time
import matplotlib.style as plot_style
import scienceplots

class SerialHandler:
    def __init__(self):
        self.serial_port = None
        self.port_list = []
        self.setup_serial()

    def setup_serial(self):
        ports = list_ports.comports()
        self.port_list = [port.name for port in ports]
        if len(ports)-1:
            while True:
                print(f"Ports available: {self.port_list}")
                choice = input(f"elegi un puerto (index de 0 a n):")
                if choice < len(self.port_list):
                    port = self.port_list[choice]
                    ports[0] = port
                    break
        self.serial_port = serial.Serial(
            port=self.port_list[0], baudrate=9600, timeout=2
        )

    def connect(self):
        self.serial_port = serial.Serial(
            port=self.port_list[0], baudrate=9600, timeout=2
        )
        if self.serial_port:
            self.serial_port.open()
            print(f"Connected to {self.port_list[0]}")
        else:
            print("No serial port available.")

    def read_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                data = self.serial_port.readline().decode('utf-8').strip().strip('\x00').split('|')[1]
                return data
            except (ValueError, IndexError):
                print("Error reading data from serial port.")
        else:
            print("Serial port not opened.")
        return None

    def write_data(self, data: int):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
            try:
                self.serial_port.write(str(data).encode())
            except Exception as e:
                print(f"Error writing data to serial port: {e}")
        else:
            print("Serial port not opened.")

    def close_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Serial port closed.")
        else:
            print("Serial port not opened.")

try:
    plot_style.use(['science', 'dark_background'])
except:
    plot_style.use('dark_background')

class PlotGUI:
    def __init__(self, serial_handler):
        self.serial_handler: SerialHandler = serial_handler
        self.root = tk.Tk()
        self.root.title("Plot Example")
        self.root.geometry("800x450")

        # Apply the Flatly theme
        style = Style(theme='darkly')

        # Create a figure and axes
        self.fig = Figure(figsize=(5, 3), facecolor='#333333')
        self.ax = self.fig.add_subplot(111)

        # Generate initial sample data
        self.x_data = [0]
        self.y_data = [0]
        self.x = np.linspace(0, 10, 100)
        self.y1 = self.x*0

        # Plot the initial data on the same axes
        self.line1, = self.ax.plot(self.x, self.y1, color='#ff9900', label='Signal')
        self.line2, = self.ax.plot([0, 1000], [1.0, 1.0], color='#ff2900', label='Ref')
        self.line3, = self.ax.plot([], [], color='g', markevery=slice(1, None, 2), linestyle='-', marker='d', label='Control')        
        # Set axis background color
        self.ax.set_facecolor('#333333')
        self.ax.set_ylim([-1.5, 1.5])

        self.ax.legend(loc='upper left')

        # Create a canvas widget and add the figure to it
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.setup_controls()
        # Create the animation
        self.ani = animation.FuncAnimation(self.fig, self.update_plots, fargs=(self.reference_value.get(),), interval=100, blit=True)

    def setup_controls(self):
        # Create a frame for the controls
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Create a label and combobox for plot options
        plot_option_label = ttk.Label(controls_frame, text="Options:")
        plot_option_label.grid(row=0, column=0, padx=5, pady=5)

        plot_option = tk.DoubleVar(value=1.0)
        plot_options = self.serial_handler.port_list
        plot_combobox = ttk.Combobox(controls_frame, textvariable=plot_option, 
                                     values=plot_options, state='readonly')
        plot_combobox.set(self.serial_handler.port_list[0])
        plot_combobox.grid(row=1, column=0, padx=5, pady=5)

        # Create a label and entry for the reference value
        reference_label = ttk.Label(controls_frame, text="Reference:")
        reference_label.grid(row=0, column=1, padx=5, pady=5)

        self.reference_value = tk.DoubleVar(value=1.0)
        reference_entry = ttk.Entry(controls_frame, textvariable=self.reference_value)
        reference_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        reference_slider = ttk.Scale(controls_frame, from_=-5.0, to=5.0, orient=tk.HORIZONTAL,
                                      variable=self.reference_value, command=self.update_plots)
        reference_slider.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # Create a button to export data
        update_button = ttk.Button(controls_frame, text="Export", 
                                   command=lambda: self.update_plots(self.reference_value.get()), 
                                   style='primary.Outline.TButton')
        update_button.grid(row=0, column=4, rowspan=3, padx=5, pady=10)

        # Create a button to connect to the serial port
        connect_button = ttk.Button(controls_frame, text="Connect", command=self.serial_handler.connect,
                                    style='primary.Outline.TButton')
        connect_button.grid(row=0, column=5, rowspan=3, padx=5, pady=10)

        controls_frame.grid_columnconfigure(0, weight=1)  # Add weight to the left column
        controls_frame.grid_columnconfigure(4, weight=1)  # Add weight to the right column

    def update_limits(self, value):
        '''TODO: add a way to modify the limits from the screen'''
        pass
        self.ax.set_ylim()

    def export_data(self):
        '''TODO: '''
        pass

    def update_plots(self, frame, value):
        value_to_send: int = self.reference_value.get()*1000
        self.serial_handler.write_data(value_to_send)
        print('sent:',value_to_send)
        data = self.serial_handler.read_data()
        if data:
            data_raw = float(data)
            print('got:', data)
            
            new_x = self.x_data[-1] + 0.1  
            new_y = data_raw / 1000  

            # Append the new data points
            self.x_data.append(new_x)
            self.y_data.append(new_y)
            value = self.reference_value.get()
            y2 = np.ones(2) * self.reference_value.get()

            # Update the plot data
            self.line1.set_data(self.x_data, self.y_data)
            self.line2.set_ydata(y2)

            if (self.y_data[-1]-value) > 0:
                self.line3.set_marker('v')
            else:
                self.line3.set_marker('^')
            line3_x = [new_x, new_x]
            line3_y = [self.y_data[-1], self.y_data[-1]-0.3*(self.y_data[-1]-value)] # change second item to be proportional to the difference between u and u_eq
            self.line3.set_data(line3_x, line3_y)
            # Adjust the x-axis limits to show only the last 50 data points
            self.ax.set_xlim(new_x - 15, new_x + 0.5)

        return self.line1, self.line2, self.line3

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    serialhand = SerialHandler()
    gui = PlotGUI(serial_handler=serialhand)
    gui.run()
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
#import scienceplots

try:
    plot_style.use(['science','dark_background'])
except:
    plot_style.use('dark_background')

root = tk.Tk()
root.title("Plot Example")
root.geometry("800x450")

# Apply the Flatly theme
style = Style(theme='darkly')

# Create a figure and axes
fig = Figure(figsize=(5, 3), facecolor='#333333')
ax = fig.add_subplot(111)

# Generate initial sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Plot the initial data on the same axes
line1, = ax.plot(x, y1, color='#ff9900', label='Signal')
line2, = ax.plot([0, 1000], [1.0,1.0], color='#ff2900', label='Ref')

# Set axis background color
ax.set_facecolor('#333333')
ax.set_ylim([-10, 110])
# Add a legend
ax.legend(loc='upper left')

# Serial stuff
ports = list_ports.comports()
port_list = [port.name for port in ports]
if len(ports)-1:
    while True:
        print(f"Ports available: {port_list}")
        choice = input(f"elegi un puerto (index de 0 a n):")
        if choice < len(port_list):
            port = port_list[choice]
            ports[0] = port
            break

# Create a canvas widget and add the figure to it
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

serialPort = serial.Serial(
    port=port_list[0], baudrate=9600, timeout=2
)
# Function to update the plots
serialPort.flushInput()
serialPort.flushOutput()
def update_plots(frame, value):
    serialPort.flush()
    int_val: int = reference_value.get()
    print('val: ', int_val)
    serialPort.write(str(int_val).encode())
    data = serialPort.readline()
    data_raw = data.decode('utf-8').strip().strip('\x00').split('|')[0]
    print('read:', data_raw)
    
    # Generate new data points
    frequency = 1  # Vary the frequency
    amplitude = np.random.uniform(0.9,1.1)  # Vary the amplitude
    new_x = x_data[-1] + 0.1  # Increment x
    new_y = float(data_raw)#/1000#amplitude * np.sin(new_x * frequency)

    # Append the new data points
    x_data.append(new_x)
    y_data.append(new_y)
    y2 = np.ones(2)*reference_value.get()
    # Update the plot data
    line1.set_data(x_data, y_data)
    
    line2.set_ydata(y2)
    # Adjust the x-axis limits to show only the last 50 data points
    ax.set_xlim(new_x - 15, new_x + 0.5)
    return line1, line2

x_data = [0]
y_data = [0]

# Create a frame for the controls
controls_frame = ttk.Frame(root)
controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# Create a label and combobox for plot options
plot_option_label = ttk.Label(controls_frame, text="Options:")
plot_option_label.grid(row=0, column=0, padx=5, pady=5)

plot_option = tk.DoubleVar(value=1.0)
plot_options = [1.0, 2.0, 3.0]
plot_combobox = ttk.Combobox(controls_frame, textvariable=plot_option, values=plot_options, state='readonly')
plot_combobox.set(1.0)
plot_combobox.grid(row=1, column=0, padx=5, pady=5)

# Create a label and entry for a number
'''num_entry_label = ttk.Label(controls_frame, text="Reference:")
num_entry_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')

num_entry = ttk.Entry(controls_frame)
num_entry.insert(0, '1.0')
num_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
'''
# Create a label and slider for the reference value
reference_label = ttk.Label(controls_frame, text="Reference:")
reference_label.grid(row=0, column=1, padx=5, pady=5)

reference_value = tk.DoubleVar(value=1.0)
reference_entry = ttk.Entry(controls_frame, textvariable=reference_value)
reference_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

reference_slider = ttk.Scale(controls_frame, from_=0.0, to=5.0, orient=tk.HORIZONTAL, variable=reference_value, command=update_plots)
reference_slider.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

# Create a button to update the plots
update_button = ttk.Button(controls_frame, text="Export", 
                           command=lambda: update_plots(reference_value.get()), 
                           style='primary.Outline.TButton')
update_button.grid(row=0, column=4, rowspan=3, padx=5, pady=10)
# Create a button to update the plots
connect_button = ttk.Button(controls_frame, text="Connect", command=update_plots,
                            style='primary.Outline.TButton')
connect_button.grid(row=0, column=5, rowspan=3, padx=5, pady=10)

controls_frame.grid_columnconfigure(0, weight=1)  # Add weight to the left column
controls_frame.grid_columnconfigure(4, weight=1)  # Add weight to the right column

# Create the animation
ani = animation.FuncAnimation(fig, update_plots, fargs=(reference_value.get(),), interval=100, blit=True)

# Start the Tkinter event loop
root.mainloop()
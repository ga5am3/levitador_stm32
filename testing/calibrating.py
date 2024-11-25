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
import matplotlib.pyplot as plt

class SerialHandler:
    def __init__(self):
        self.serial_port = None
        self.port_list = []
        self.setup_serial()

    def setup_serial(self):
        ports = list_ports.comports()
        self.port_list = [port.device for port in ports]
        if self.port_list:
            self.serial_port = serial.Serial(self.port_list[0], 9600, timeout=1)

    def read_serial(self):
        if self.serial_port and self.serial_port.in_waiting:
            data = self.serial_port.readline().decode('utf-8').strip()
            h_prom, h, h_hat = map(int, data.split())
            return h_prom, h / 10000.0, h_hat / 10000.0
        return None, None, None

class CalibrationHandler:
    def __init__(self):
        self.calibration_points = {}

    def add_calibration_point(self, x, y):
        if y not in self.calibration_points:
            self.calibration_points[y] = []
        self.calibration_points[y].append(x)

    def calculate_best_fit(self):
        x_values = []
        y_values = []
        for y, x_list in self.calibration_points.items():
            best_x = min(x_list, key=lambda x: abs(y - x))
            x_values.append(best_x)
            y_values.append(y)
        if len(x_values) >= 2:
            self.m, self.b = np.polyfit(x_values, y_values, 1)
        else:
            self.m, self.b = 1, 0

    def calibrate(self, x):
        return self.m * x + self.b

class CalibrationApp:
    def __init__(self, root):
        self.root = root
        self.serial_handler = SerialHandler()
        self.calibration_handler = CalibrationHandler()
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Calibration Interface")
        self.style = Style(theme='darkly')

        self.frame = ttk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.label_x = ttk.Label(self.frame, text="Measured Value (x):")
        self.label_x.grid(row=0, column=0, padx=5, pady=5)
        self.entry_x = ttk.Entry(self.frame)
        self.entry_x.grid(row=0, column=1, padx=5, pady=5)

        self.label_y = ttk.Label(self.frame, text="Real Value (y):")
        self.label_y.grid(row=1, column=0, padx=5, pady=5)
        self.entry_y = ttk.Entry(self.frame)
        self.entry_y.grid(row=1, column=1, padx=5, pady=5)

        self.button_add = ttk.Button(self.frame, text="Add Calibration Point", command=self.add_calibration_point)
        self.button_add.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.button_calculate = ttk.Button(self.frame, text="Calculate Best Fit", command=self.calculate_best_fit)
        self.button_calculate.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.label_calibrated = ttk.Label(self.frame, text="Calibrated Value:")
        self.label_calibrated.grid(row=4, column=0, padx=5, pady=5)
        self.label_calibrated_value = ttk.Label(self.frame, text="")
        self.label_calibrated_value.grid(row=4, column=1, padx=5, pady=5)

        self.update_calibrated_value()

    def add_calibration_point(self):
        x = float(self.entry_x.get())
        y = float(self.entry_y.get())
        self.calibration_handler.add_calibration_point(x, y)
        self.entry_x.delete(0, tk.END)
        self.entry_y.delete(0, tk.END)

    def calculate_best_fit(self):
        self.calibration_handler.calculate_best_fit()

    def update_calibrated_value(self):
        h_prom, h, h_hat = self.serial_handler.read_serial()
        if h is not None:
            calibrated_value = self.calibration_handler.calibrate(h)
            self.label_calibrated_value.config(text=f"{calibrated_value:.2f}")
        self.root.after(1000, self.update_calibrated_value)

def plot_signals():
    serial_handler = SerialHandler()
    fig, ax = plt.subplots()
    h_prom_data, h_data, h_hat_data = [], [], []

    def update(frame):
        h_prom, h, h_hat = serial_handler.read_serial()
        if h_prom is not None:
            h_prom_data.append(h_prom)
            h_data.append(h)
            h_hat_data.append(h_hat)
            ax.clear()
            ax.plot(h_prom_data, label='h_prom')
            ax.plot(h_data, label='h')
            ax.plot(h_hat_data, label='h_hat')
            ax.legend()
            ax.set_xlabel('Time')
            ax.set_ylabel('Values')
            ax.set_title('Real-time Sensor Data')

    ani = animation.FuncAnimation(fig, update, interval=1000)
    plt.show()

if __name__ == "__main__":
    #root = tk.Tk()
    #app = CalibrationApp(root)
    #root.mainloop()
    plot_signals()
import tkinter as tk
import matplotlib.animation as animation
from serial_handler import SerialHandler
from plotter import Plotter
from gui import GUI
from config import *

class SerialPlotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.serial_handler = SerialHandler()
        self.plotter = Plotter()
        self.gui = GUI(self.root, self.plotter, self.update_plots)
        
        # Initialize serial port
        self.serial_handler.initialize_port()
        
        # Create animation
        self.ani = animation.FuncAnimation(
            self.plotter.fig,
            self.update_plots,
            fargs=(self.gui.reference_value.get(),),
            interval=PLOT_UPDATE_INTERVAL,
            blit=True
        )
        
    def update_plots(self, frame, value=None):
        """Update plot with new data from serial port."""
        value = self.gui.reference_value.get()
        print(f"Reference value: {value}")
        # Write reference value to serial port
        self.serial_handler.write_data(value)
        
        # Read new data from serial port
        new_y = self.serial_handler.read_data()
        if new_y is not None:
            print(f"New data: {new_y}") 
            return self.plotter.update(new_y, value)

        return self.plotter.line1, self.plotter.line2
        
    def run(self):
        """Start the application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = SerialPlotApp()
    app.run()
import tkinter as tk
import csv
import matplotlib.animation as animation
from serial_handler import SerialHandler
from plotter import Plotter
from gui import GUI
from config import *
from datetime import datetime

class SerialPlotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.serial_handler = SerialHandler()
        self.plotter = Plotter()
        self.gui = GUI(self.root, self.plotter, self.update_plots, self.export_data)
        
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
        
        # Read list from serial port
        y_values = self.serial_handler.read_data()
        if y_values:
            print(f"New data: {y_values}")
            return self.plotter.update(y_values, value)

        return self.plotter.line1, self.plotter.line2, self.plotter.line3
    
    def export_data(self):
        """Export the collected data to a CSV file."""
        filename = f"exported_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Signal 1", "Signal 2"])  # Header row
                for x, y1, y2 in zip(self.plotter.x_data, self.plotter.y_data, self.plotter.y_data2):
                    writer.writerow([x, y1, y2])
            print(f"Data successfully exported to {filename}")
        except Exception as e:
            print(f"Error exporting data: {e}")
        
    def run(self):
        """Start the application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = SerialPlotApp()
    app.run()
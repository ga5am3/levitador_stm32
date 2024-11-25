# plotter.py
"""Module for handling plot creation and updates."""
import numpy as np
from matplotlib.figure import Figure
from config import PLOT_FIGSIZE, PLOT_BGCOLOR, SIGNAL_COLOR, REFERENCE_COLOR, Y_AXIS_LIMITS, X_AXIS_WINDOW, DEFAULT_REFERENCE

class Plotter:
    def __init__(self):
        # Create figure and axes
        self.fig = Figure(figsize=PLOT_FIGSIZE, facecolor=PLOT_BGCOLOR)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(PLOT_BGCOLOR)
        self.ax.set_ylim(Y_AXIS_LIMITS)
        
        # Initialize data
        self.x_data = [0]
        self.y_data = [0]
        
        # Create plot lines
        self.line1, = self.ax.plot([], [], color=SIGNAL_COLOR, label='Signal')
        self.line2, = self.ax.plot([0, 1000], [DEFAULT_REFERENCE, DEFAULT_REFERENCE], 
                                 color=REFERENCE_COLOR, label='Ref')
        
        self.ax.legend(loc='upper left')
        
    def update(self, new_y, reference_value):
        """Update plot with new data."""
        new_x = self.x_data[-1] + 0.1
        self.x_data.append(new_x)
        self.y_data.append(new_y)
        
        # Update plot lines
        self.line1.set_data(self.x_data, self.y_data)
        self.line2.set_ydata(np.ones(2) * reference_value)
        
        # Update x-axis limits
        self.ax.set_xlim(new_x - X_AXIS_WINDOW, new_x + 0.5)
        
        return self.line1, self.line2
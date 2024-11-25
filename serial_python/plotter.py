# plotter.py
"""Module for handling plot creation and updates."""
import numpy as np
from matplotlib.figure import Figure
from config import PLOT_FIGSIZE, PLOT_BGCOLOR, SIGNAL_COLOR, REFERENCE_COLOR, Y_AXIS_LIMITS, X_AXIS_WINDOW, DEFAULT_REFERENCE

class Plotter:
    """A class used to represent a Plotter for real-time data visualization. Attributes
    ----------
    fig : Figure
        The matplotlib figure object.
    ax : Axes
        The axes object of the figure.
    x_data : list
        List to store x-axis data points.
    y_data : list
        List to store y-axis data points for the first signal.
    y_data2 : list
        List to store y-axis data points for the second signal.
    line1 : Line2D
        Line object for the first signal plot.
    line2 : Line2D
        Line object for the reference plot.
    line3 : Line2D
        Line object for the second signal plot.
    Methods 
    __init__():
        Initializes the plotter object, sets up the figure and axes for plotting, 
        initializes the data lists for the x and y coordinates, and creates the plot lines.
    update(y_values, reference_value):
        Updates the plot with new data."""

    def __init__(self):
        """
        Initializes the plotter object.
        This method sets up the figure and axes for plotting, initializes the data
        lists for the x and y coordinates, and creates the plot lines for the signals
        and reference.
        Attributes:
            fig (Figure): The matplotlib figure object.
            ax (Axes): The axes object of the figure.
            x_data (list): List to store x-axis data points.
            y_data (list): List to store y-axis data points for the first signal.
            y_data2 (list): List to store y-axis data points for the second signal.
            line1 (Line2D): Line object for the first signal plot.
            line2 (Line2D): Line object for the reference plot.
            line3 (Line2D): Line object for the second signal plot.
        """
        # Create figure and axes
        self.fig = Figure(figsize=PLOT_FIGSIZE, facecolor=PLOT_BGCOLOR)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(PLOT_BGCOLOR)
        self.ax.set_ylim(Y_AXIS_LIMITS)
        
        # Initialize data
        self.x_data = [0]
        self.y_data = [0]
        self.y_data2 = [0]
        
        # Create plot lines
        self.line1, = self.ax.plot([], [], color=SIGNAL_COLOR, label='Signal 1')
        self.line2, = self.ax.plot([0, 1000], [DEFAULT_REFERENCE, DEFAULT_REFERENCE], 
                                 color=REFERENCE_COLOR, label='Ref')
        self.line3, = self.ax.plot([], [], color='blue', label='Signal 2')
        self.ax.legend(loc='upper left')

    def update(self, y_values, reference_value):
        """
        Update the plot with new data.
        Parameters:
        y_values (list): A list of new y-values to be plotted. The first element is used for the primary y-axis data.
                         If there is a second element, it is used for the secondary y-axis data.
        reference_value (float): A reference value to be plotted as a horizontal line.
        Returns:
        tuple: A tuple containing the updated line objects (line1, line2, line3).
        """
        """Update plot with new data."""

        new_x = self.x_data[-1] + 0.1
        self.x_data.append(new_x)
        self.y_data.append(y_values[0])
        if len(y_values) > 1:
            self.y_data2.append(y_values[1])
        # Update plot lines
        self.line1.set_data(self.x_data, self.y_data)
        self.line3.set_data(self.x_data, self.y_data2)
        self.line2.set_ydata(np.ones(2) * reference_value)
        # Update x-axis limits
        self.ax.set_xlim(new_x - X_AXIS_WINDOW, new_x + 0.5)
        
        return self.line1, self.line2, self.line3
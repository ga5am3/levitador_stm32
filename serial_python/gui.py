"""Module for handling the GUI components."""
import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from typing import Callable
from plotter import Plotter
from config import APP_TITLE, WINDOW_SIZE, THEME, REFERENCE_MIN, REFERENCE_MAX

class GUI:
    def __init__(self, root: tk.Tk, plotter: Plotter, 
                 on_connect: Callable, on_export: Callable = None):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.style = Style(theme=THEME)
        
        # Initialize variables
        self.reference_value = tk.DoubleVar(value=1.0)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(plotter.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create controls
        self.create_controls(on_connect, on_export)
        
    def create_controls(self, on_connect: Callable, on_export: Callable):
        """Create control panel with widgets."""
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Reference value controls
        ttk.Label(controls_frame, text="Reference:").grid(
            row=0, column=0, padx=5, pady=5
        )
        ttk.Entry(
            controls_frame, textvariable=self.reference_value
        ).grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        ttk.Scale(
            controls_frame, from_=REFERENCE_MIN, to=REFERENCE_MAX, orient=tk.HORIZONTAL,
            variable=self.reference_value
        ).grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        
        # Buttons
        ttk.Button(
            controls_frame, text="Connect", command=on_connect,
            style='primary.Outline.TButton'
        ).grid(row=0, column=1, padx=5, pady=10)
        
        ttk.Button(
            controls_frame, text="Export", command=on_export,
            style='primary.Outline.TButton'
        ).grid(row=0, column=2, padx=5, pady=10)

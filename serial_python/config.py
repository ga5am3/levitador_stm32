# config.py
"""Configuration settings for the Serial Plot application."""
import matplotlib
import matplotlib.style as plot_style

# Matplotlib Configuration
matplotlib.use('TkAgg')
try:
    plot_style.use(['science', 'dark_background'])
except:
    plot_style.use('dark_background')

# Application Settings
APP_TITLE = "Plot Example"
WINDOW_SIZE = "800x450"
THEME = "darkly"
PLOT_UPDATE_INTERVAL = 100  # milliseconds

# Serial Communication Settings
BAUDRATE = 9600
TIMEOUT = 2

# Plot Settings
PLOT_FIGSIZE = (5, 3)
PLOT_BGCOLOR = '#333333'
SIGNAL_COLOR = '#ff9900'
REFERENCE_COLOR = '#ff2900'
Y_AXIS_LIMITS = (-0, 0.25)
X_AXIS_WINDOW = 15  # seconds
FACTOR = 10000.0  # Scale factor for the signal

# Control Settings
REFERENCE_MIN = 0.50
REFERENCE_MAX = 0.10
DEFAULT_REFERENCE = 1.0
PLOT_OPTIONS = [1.0, 2.0, 3.0]

# Animation Settings
ANIMATION_INTERVAL = 100  # milliseconds
ANIMATION_SAVE_COUNT = 100  # Maximum number of frames to cache
ANIMATION_CACHE_FRAMES = False  # Disable frame caching to prevent memory issues

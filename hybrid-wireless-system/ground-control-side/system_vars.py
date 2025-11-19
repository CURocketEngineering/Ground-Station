import serial
import threading
import time
import queue
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.style as style
import sys
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np




# Serial config
SERIAL_PORT = "COM18"  # Change to XBee port 
BAUD_RATE = 115200

# Logging
LOG_FILE = f"logs/hybrid_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# Command queue to send to Teensy
command_queue = queue.Queue()

# Log queue to write logs
log_queue = queue.Queue()

# Data queue for plot
data_queue = queue.Queue()

# Global buffers and states
time_buffer = []
thrust_buffer = []
relay_state = {"FILL": 0, "PURGE": 0, "FIRE": 0}
system_state = "SAFE" # switches between SAFE and ARMED 
motor_fired = False
motor_filled = False
danger_zone_vented = False
igniter_fired = False

IMAGE_DIR = Path("resources/images")
# Layer definition
# Format: (Filename, layername, layerpriority)
LAYER_CONFIG = [
    ("motor-burn.png", "motor-burn", 15),
    ("post-burn.png", "post-burn", 14),
    ("load-cell-on.png", "load-cell-on", 13),
    ("load-cell.png", "load-cell-off", 12),
    ("laptop-in.png", "laptop-in", 11),
    ("laptop-out.png", "laptop-out", 10),
    ("fill-on.png", "fill-on", 9),
    ("purge-on.png", "purge-on", 8),
    ("fire-on.png", "fire-on", 7),
    ("n2o-venting.png", "n2o-venting", 6),
    ("n2o-motor-system.png", "n2o-motor-system", 5),
    ("n2o-danger-zone.png", "n2o-danger-zone", 4),
    ("armed.png", "armed", 3),
    ("safe.png", "safe", 2),
    ("background.png", "background", 1)
]


### Everything below is for visualization ###


# Root window
root = tk.Tk()
root.title("System Visualization")
root.geometry("1920x800")
root.attributes("-topmost", True)  # Keep window on top

# Main frame
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Canvas for background image
canvas = tk.Canvas(main_frame, bg="white")
canvas.grid(row=0, column=0, sticky=tk.NSEW)

first_image = Image.open(IMAGE_DIR / "background.png").convert("RGBA")

photo = ImageTk.PhotoImage(first_image)

# Grid configuration for main frame
main_frame.columnconfigure(0, weight=3) # Image takes 3/4 of the width
main_frame.columnconfigure(1, weight=1) # Plot takes 1/4 of the width
main_frame.rowconfigure(0, weight=1)  # Both rows take equal height

# Dictionary to hold images for each layer
images = {}

# Layer visibility control
layer_visibility = {layer_name: False for _, layer_name, _ in LAYER_CONFIG}

def load_images():
    for filename, layername, _ in LAYER_CONFIG:
        img_path = IMAGE_DIR / filename
        if not img_path.exists():
            print(f"Warning: Image {filename} not found.")
            continue
        img = Image.open(img_path).convert("RGBA")
        images[layername] = img

load_images()

def update_all_layers(event=None):
    if not canvas.winfo_width() or not canvas.winfo_height():
        return  # Prevent early call when canvas not ready

    # Start from a transparent base
    composite = Image.new("RGBA", (images["background"].width, images["background"].height), (0, 0, 0, 0))

    # Sort and render by priority
    sorted_layers = sorted(LAYER_CONFIG, key=lambda x: x[2])  # Sort by priority
    for _, layername, _ in sorted_layers:
        if layer_visibility.get(layername, False) and layername in images:
            composite = Image.alpha_composite(composite, images[layername])

    # Resize to fit canvas
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    resized = composite.resize((canvas_width, canvas_height), Image.LANCZOS)

    # Update image on canvas
    photo = ImageTk.PhotoImage(resized)
    canvas.image = photo  # Prevent garbage collection
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    #canvas.config(width=canvas_width, height=canvas_height)

canvas.bind("<Configure>", update_all_layers)

# Matplotlib setup
style.use("ggplot")  # Use ggplot style for better aesthetics
fig = Figure(figsize=(5, 10), dpi=100)
ax = fig.add_subplot(111)
xdata, ydata = [], []
line, = ax.plot([], [], 'r-')
# ax.set_xlim(0, 100)
# ax.set_ylim(-1.5, 1.5)
#canvas.create_image(0, 0, anchor=tk.NW, image=photo)
ax.set_title("Load Cell Live Thrust")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Thrust (N)")

x = np.linspace(0, 10, 100)
y = np.sin(x)
ax.plot(x, y)

canvas_plot = FigureCanvasTkAgg(fig, master=main_frame)
plot_widget = canvas_plot.get_tk_widget()
plot_widget.grid(row=0, column=1, sticky="nsew")

# Allow plot to also resize with window
def update_plot_size(event):
    fig.set_size_inches(event.width / 100, event.height / 100)
    canvas_plot.draw()

plot_widget.bind("<Configure>", update_plot_size)

is_topmost = True

def toggle_topmost(event=None):
    global is_topmost
    is_topmost = not is_topmost
    root.attributes("-topmost", is_topmost)
    print(f"Topmost mode {'enabled' if is_topmost else 'disabled'}.")

root.bind("<F12>", toggle_topmost)
       
def start_ui():
    #root.after(100, user_input_thread_start)
    root.mainloop()
    
def stop_ui():
    """Stop the UI loop."""
    root.quit()
    root.destroy()

### All dynamic layer functions and state logic/animation below ###

def set_motor_fired_state(state):
    global motor_fired
    print("\t\t[ℹ] motor_fired_state set to", state)
    motor_fired = state
    
def set_motor_filled_state(state):
    global motor_filled
    print("\t\t[ℹ] motor_filled_state set to", state)
    motor_filled = state

def set_igniter_fired_state(state):
    global igniter_fired
    print("\t\t[ℹ] igniter_fired_state set to", state)
    igniter_fired = state
    
def set_danger_zone_vented_state(state):
    global danger_zone_vented
    print("\t\t[ℹ] danger_zone_vented_state set to", state)
    danger_zone_vented = state

def show_layer(layer_name):
    if layer_name not in layer_visibility:
        print(f"\t[❗] Bug: Layer {layer_name} does not exist.")
        return
    layer_visibility[layer_name] = True
    update_all_layers()

def hide_layer(layer_name):
    if layer_name not in layer_visibility:
        print(f"\t[❗] Bug: Layer {layer_name} does not exist.")
        return
    layer_visibility[layer_name] = False
    update_all_layers()

def visualize_safe_mode():
    show_layer("safe")
    hide_layer("armed")
    
def visualize_armed_mode():
    show_layer("armed")
    hide_layer("safe")
    
def visualize_fill_relay_on():
    show_layer("fill-on")
    show_layer("n2o-motor-system")
    print("visualize_fill_relay_on called")
    if not motor_fired:
        print("Motor not fired, showing motor system filling.")
        set_motor_filled_state(True)

def visualize_fill_relay_off():
    hide_layer("fill-on")
    if motor_fired:
        hide_layer("n2o-motor-system")
    
def visualize_purge_relay_on():
    show_layer("purge-on")
    if motor_filled:
        show_layer("n2o-venting")
        set_motor_filled_state(False)
        root.after(2000, hide_layer, "n2o-venting") # Hide after 2 seconds
    hide_layer("n2o-motor-system")
    
def visualize_purge_relay_off():
    hide_layer("purge-on")
    
def visualize_fire_relay_on():
    show_layer("fire-on")
    if igniter_fired:
        return
    set_igniter_fired_state(True)
    if motor_filled:
        show_layer("motor-burn")
        set_motor_fired_state(True)
        root.after(5000, hide_layer, "motor-burn")  # Hide after 5 seconds
    show_layer("post-burn")
    hide_layer("n2o-motor-system")
    
def visualize_fire_relay_off():
    hide_layer("fire-on")
    

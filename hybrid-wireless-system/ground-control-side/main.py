from system_vars import *
from system_handler import *
from data_handler import *


if __name__ == "__main__":
    print("[ℹ] Hybrid Motor Ground Control System is running.")
    print("[ℹ] Use the command line to control the system and visualize live data.")
    print("[ℹ] Type 'quit-f' to force quit the program at any time. (Not recommended if you do not know what you are doing with this command!)")

    # Start threads
    serial_thread_start()

    show_layer("background")
    show_layer("n2o-danger-zone")
    
    enter_safe_mode()
    
    user_input()
    
    # Start the UI for system visualization
    start_ui()
    
    


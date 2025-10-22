from system_vars import *

def user_input():
    global system_state
    # map of commands and what state you can use them in (SAFE, ARMED, ANY)
    command_states = {
        "ARM": "SAFE",
        "SAFE": "ARMED",
        "PURGE": "SAFE",
        "FILL": "ARMED",
        "FIRE": "ARMED",
        "DUMP": "SAFE",
        "ABORT": "ANY",
        "QUIT": "SAFE"
    }
    
    while True:
        # print only available commands in the current state
        available_commands = [cmd for cmd, allowed_state in command_states.items() if allowed_state == system_state or allowed_state == "ANY"]
        print(f"[ℹ] Available commands in {system_state} state: {', '.join(available_commands)}")

        cmd = input("[⌨] Enter command: ").strip().upper()

        if cmd in available_commands:
            command_queue.put(f"CMD:{cmd}")
        elif cmd == "QUIT-F":
            print("\t[ℹ] Force quitting program.")
            command_queue.put("CMD:FORCEQUIT")
            quit_program(force_quit=True)
        elif cmd in command_states:
            print(f"\t[⚠] Command '{cmd}' not available in current state '{system_state}'.")
        else:
            print(f"\t[⚠] Invalid command: '{cmd}'. Please try again.") 

        # if command queue is not empty, process the first command
        if not command_queue.empty():
            command = command_queue.get()
            #print(f"\t[ℹ] Processing command: {command}")
            process_command(command)  

def user_input_thread_start():
    """Reference function for starting the user input thread."""
    input_thread = threading.Thread(target=user_input, daemon=True)
    input_thread.start()
            
def process_command(command):
    global system_state
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_queue.put(f"{timestamp} | CMD_SENT | {command}")
    # Log the command with timestamp
    if command == "CMD:ARM":
        enter_armed_mode()
    elif command == "CMD:SAFE":
        enter_safe_mode()
    elif command == "CMD:PURGE":
        # Toggle purge relay
        if relay_state["PURGE"] == 0:
            open_purge_relay()
        else:
            close_purge_relay()
        print(f"\t[ℹ] Purge relay toggled to {'ON' if relay_state['PURGE'] else 'OFF'}.")
    elif command == "CMD:FILL":
        # Toggle fill relay
        if relay_state["FILL"] == 0:
            open_fill_relay()
        else:
            close_fill_relay()
        print(f"\t[ℹ] Fill relay toggled to {'ON' if relay_state['FILL'] else 'OFF'}.")
    elif command == "CMD:FIRE":
        print("\t[ℹ] Are you sure you want to fire? (yes/no)")
        response = input().strip().lower()
        if response == "yes":
            print("\t[ℹ] Proceeding with fire cycle.")
            fire_cycle()
        elif response == "no":
            print("\t[ℹ] Cancelling fire cycle.")
            return
    elif command == "CMD:ABORT":
        close_purge_relay()
        enter_safe_mode()
        print("\t[ℹ] System aborted. All relays off.")
    elif command == "CMD:DUMP":
        print("[⌨] Are you sure you want to dump the nitrous? (yes/no)")
        response = input().strip().lower()
        if response == "yes":
            dump_nitrous()
        elif response == "no":
            print("\t[ℹ] Cancelling dump.")
        else:
            print("\t[⚠] Invalid response.")
            process_command("CMD:DUMP")
            # add nothing else here so the system can recurse until a valid response
    elif command == "CMD:QUIT":
        quit_program()

def enter_safe_mode():
    global system_state
    if system_state != "SAFE":
        print("\t[ℹ] Entering safe mode.")
    system_state = "SAFE"
    close_fill_relay()
    visualize_safe_mode()

def enter_armed_mode():
    global system_state
    if system_state != "ARMED":
        print("\t[ℹ] Entering armed mode.")
    system_state = "ARMED"
    close_purge_relay()
    visualize_armed_mode()

def close_purge_relay():
    global relay_state
    if relay_state["PURGE"] == 1:
        print("\t[ℹ] Closing purge relay.")
    relay_state["PURGE"] = 0  # Close purge relay
    visualize_purge_relay_off()  # Update UI to show purge relay is closed

def open_purge_relay():
    global relay_state
    if relay_state["PURGE"] == 0:
        print("\t[ℹ] Opening purge relay.")
    relay_state["PURGE"] = 1  # Open purge relay
    visualize_purge_relay_on()  # Update UI to show purge relay is open

def close_fill_relay():
    global relay_state
    if relay_state["FILL"] == 1:
        print("\t[ℹ] Closing fill relay.")
    relay_state["FILL"] = 0  # Close fill relay
    visualize_fill_relay_off()

def open_fill_relay():
    global relay_state, motor_filled
    if relay_state["FILL"] == 0:
        print("\t[ℹ] Opening fill relay.")
    relay_state["FILL"] = 1  # Open fill relay
    visualize_fill_relay_on()  # Update UI to show fill relay is open
    print (f"global motor filled state: {motor_filled}")

def open_fire_relay():
    global relay_state
    if relay_state["FIRE"] == 0:
        print("\t[ℹ] Opening fire relay.")
    relay_state["FIRE"] = 1  # Open fire relay
    visualize_fire_relay_on()  # Update UI to show fire relay is open
    
def close_fire_relay():
    global relay_state
    if relay_state["FIRE"] == 1:
        print("\t[ℹ] Closing fire relay.")
    relay_state["FIRE"] = 0  # Close fire relay
    visualize_fire_relay_off()  # Update UI to show fire relay is closed

def fire_cycle():
    global relay_state
    if system_state == "ARMED":
        open_fire_relay()  # Activate fire relay
        root.after(3000, close_fire_relay) # Close fire relay after 3 seconds
        root.after(3000, close_fill_relay) # Close fill relay after 3 seconds
        time.sleep(5)  # Wait 5 seconds before returning control to the user to allow the fire cycle to complete
    else :
        print("\t[⚠] Warning: This function should not be called unless the system is armed.")

def dump_nitrous():
    print("[⌨] Is the nitrous tank valve closed? (yes/no)")
    response = input().strip().lower()
    if response == "yes":
        print("\t[ℹ] Nitrous tank valve is closed. Dumping idle nitrous between bottle and fill valve.")
        # loop between the fill and purge valves to dump the nitrous
        for _ in range(5):  # Adjust the number of dumps as needed
            time.sleep(1)  # Wait before the next dump
            open_fill_relay()
            time.sleep(1)  # Wait for a short period to allow filling
            close_fill_relay()
            time.sleep(1)  # Wait before the next dump
            open_purge_relay()
            time.sleep(1)  # Wait for a short period to allow purging
            close_purge_relay()
        print("\t[ℹ] Nitrous dump complete.")
    elif response == "no":
        print("\t[ℹ] Cancelling dump.")
    else:
        print("\t[⚠] Invalid response.")
        dump_nitrous()  # Recurse until a valid response

def quit_program(force_quit=False):
    if not force_quit:
        # Ask if they need to dump nitrous before quitting
        print("[⌨] Do you need to dump the nitrous before quitting? (yes/no)")
        response = input().strip().lower()
        if response == "yes":
            dump_nitrous()
        elif response == "no":
            print("\t[ℹ] Not dumping nitrous.")
        else:
            print("\t[⚠] Invalid response.")
            quit_program()  # Recurse until a valid response

        # Do you still want to quit?
        print("[⌨] Do you still want to quit? (yes/no)")
        response = input().strip().lower()
        if response == "no":
            print("\t[ℹ] Cancelling quit.")
            return  # Return to allow further commands
        elif response != "yes":
            print("\t[⚠] Invalid response. Cancelling quit.")
            return

        print("[ℹ] Exiting program.")
        close_purge_relay()
        for i in range(5):
            print(f"\t[ℹ] Closing program in {5-i} seconds...")
            time.sleep(1)
        plt.close()
        stop_ui()
        time.sleep(2)
        sys.exit(0)
    else:
        print("[ℹ] Force quitting program.")
        plt.close()
        stop_ui()
        close_purge_relay()
        time.sleep(2)
        sys.exit(0)

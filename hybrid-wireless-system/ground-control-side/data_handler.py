from system_vars import *

def animate(i):
    while not data_queue.empty():
        t, thrust = data_queue.get()
        time_buffer.append(t - time_buffer[0] if time_buffer else 0)
        thrust_buffer.append(thrust)
        if len(time_buffer) > 300:
            time_buffer.pop(0)
            thrust_buffer.pop(0)

    ax.clear()
    ax.plot(time_buffer, thrust_buffer, label="Thrust (N)")
    ax.set_title("Hybrid Motor Test Stand Live Thrust")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Thrust (N)")
    ax.legend(loc="upper left")
    ax.grid(True)

def serial_thread():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser, open(LOG_FILE, "w") as log:
            while True:
                # 1. Read from serial and log it
                line = ser.readline().decode("utf-8").strip()
                if line:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    log_entry = f"{timestamp} | DATA_RECV | {line}"
                    print(log_entry)
                    log.write(log_entry + "\n")
                    log.flush()
                    data_queue.put(line)

                # 2. Send any commands
                if not command_queue.empty():
                    out = command_queue.get()
                    ser.write((out + "\n").encode("utf-8"))

                # 3. Write any queued log entries (e.g., commands)
                while not log_queue.empty():
                    log_entry = log_queue.get()
                    log.write(log_entry + "\n")
                    log.flush()

    except serial.SerialException as e:
        print(f"[ERROR] Serial error: {e}")
        
def serial_thread_start():
    serial_thread_instance = threading.Thread(target=serial_thread, daemon=True)
    serial_thread_instance.start()

    

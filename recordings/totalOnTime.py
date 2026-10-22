import csv
from datetime import datetime

INPUT_FILE = "recordings/data2.csv"

# Common names for timestamp columns
TIME_COLUMNS = [
    "TIMESTAMP",
    "TIME",
    "TIMESTAMP_MS",
    "TIME_MS",
    "DATETIME",
    "DATE_TIME",
]

with open(INPUT_FILE, "r", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows")

# Find the time column
time_column = None

for column in TIME_COLUMNS:
    if column in reader.fieldnames:
        time_column = column
        break

if time_column is None:
    print("Could not find a timestamp column.")
    print("Available columns:")
    for column in reader.fieldnames:
        print(f"  {column}")
    exit()

print(f"Using time column: {time_column}")

# Get valid timestamps
timestamps = []

for row in rows:
    value = row[time_column]

    if value is None or value.strip() == "":
        continue

    try:
        # Try Unix timestamp in seconds
        timestamp = float(value)
        timestamps.append(timestamp)
    except ValueError:
        pass

if len(timestamps) < 2:
    print("Could not find enough valid timestamps.")
    exit()

# Calculate total time
start_time = min(timestamps)
end_time = max(timestamps)

total_seconds = end_time - start_time
total_seconds /= 1000  # Convert to seconds

hours = int(total_seconds // 3600)
minutes = int((total_seconds % 3600) // 60)
seconds = total_seconds % 60

print()
print("===== Recording Duration =====")
print(f"Start timestamp: {start_time}")
print(f"End timestamp:   {end_time}")
print(f"Total seconds:   {total_seconds:.2f}")
print(f"Total time:      {hours}h {minutes}m {seconds:.2f}s")
print("==============================")
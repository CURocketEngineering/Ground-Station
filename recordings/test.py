import csv

INPUT_FILE = "recordings/data2.csv"

with open(INPUT_FILE, "r", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows")

# Find the highest altitude
highest_altitude = None
highest_row = None
highest_index = None

for i, row in enumerate(rows):
    try:
        altitude = float(row["ALTITUDE"])

        if highest_altitude is None or altitude > highest_altitude:
            highest_altitude = altitude
            highest_row = row
            highest_index = i

    except (ValueError, TypeError):
        continue

if highest_altitude is None:
    print("Could not find any valid altitude values.")
else:
    print(f"Highest altitude: {highest_altitude}")
    print(f"Row: {highest_index}")
    print(f"Full row: {highest_row}")
import csv

INPUT_FILE = "recordings/data.csv"
OUTPUT_FILE = "recordings/data_trimmed.csv"

KEEP_BEFORE = 25

with open(INPUT_FILE, "r", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

print(f"Loaded {len(rows)} rows")

# Convert altitude values to numbers
altitudes = []

for row in rows:
    try:
        altitude = float(row["ALTITUDE"])
        altitudes.append(altitude)
    except (ValueError, TypeError):
        altitudes.append(None)

# Find where altitude starts increasing
start_index = None

for i in range(1, len(altitudes)):
    if altitudes[i] is None or altitudes[i - 1] is None:
        continue

    if altitudes[i] > altitudes[i - 1]:
        start_index = i
        break

if start_index is None:
    print("Could not find altitude increase.")
    exit()

# Keep 25 rows before altitude starts increasing
trim_index = max(0, start_index - KEEP_BEFORE)

print(f"Altitude begins increasing at row: {start_index}")
print(f"Keeping 25 rows before it.")
print(f"Removing rows 0 through {trim_index - 1}")

trimmed_rows = rows[trim_index:]

# Write cleaned file
with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(trimmed_rows)

print(f"Done!")
print(f"Original rows: {len(rows)}")
print(f"Remaining rows: {len(trimmed_rows)}")
print(f"Saved to: {OUTPUT_FILE}")

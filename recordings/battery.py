import csv

INPUT_FILE = "recordings/data2.csv"
OUTPUT_FILE = "battery_values.txt"

with open(INPUT_FILE, "r", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

battery_values = []

for i, row in enumerate(rows):
    batt_value = row.get("BATT", "").strip()

    # Ignore empty BATT cells
    if batt_value == "":
        continue

    try:
        battery = float(batt_value)
    except (ValueError, TypeError):
        continue

    battery_values.append((battery, i))

# Keep original CSV order
with open(OUTPUT_FILE, "w") as f:
    for battery, index in battery_values:
        f.write(f"BATT: {battery} | Row: {index}\n")

print(f"Wrote {len(battery_values)} battery values to {OUTPUT_FILE}")
from cure_ground.core.protocols.data_names.data_name_loader import load_data_name_enum


class TextFormatterRadio:
    def __init__(self, protocol_version: int = 3):
        self.data_names = load_data_name_enum(protocol_version)

        self.units = {
            item["name"]: item.get("unit", "")
            for item in self.data_names.data_definitions
        }

        self.categories = {
            "accelerometer": [],
            "gyroscope": [],
            "magnetometer": [],
            "environment": [],
            "telemetry": [],
        }
        for item in self.data_names.data_definitions:
            name = item["name"]
            lname = name.lower()

            if "accelerometer_" in lname:
                self.categories["accelerometer"].append(name)

            elif "gyroscope_" in lname:
                self.categories["gyroscope"].append(name)

            elif "magnetometer_" in lname:
                self.categories["magnetometer"].append(name)

            elif lname in ["temperature", "pressure", "altitude"]:
                self.categories["environment"].append(name)

            else:
                self.categories["telemetry"].append(name)

        self.categories["packets"] = ["NUM_PACKETS_SENT"]

    def get_left_column_text(self, status_data):
        parts = []
        for cat in ["accelerometer", "gyroscope", "magnetometer", "environment"]:
            parts.append(self._format_category(cat, status_data))
        return "<br><br>".join(parts)

    def get_right_column_text(self, status_data):
        telem = self._format_category("telemetry", status_data)
        packets = self._format_category("packets", status_data)
        return telem + "<br><br>" + packets

    def _format_category(self, category: str, status_data) -> str:
        lines = [f"<b>-- {category.capitalize()} --</b>"]

        for key in self.categories.get(category, []):
            value = status_data.get(key, "N/A")
            unit = self.units.get(key, "")

            if unit:
                lines.append(f"<b>{key}:</b> <b>{value}</b> {unit}")
            else:
                lines.append(f"<b>{key}:</b> <b>{value}</b>")

        return "<br>".join(lines)

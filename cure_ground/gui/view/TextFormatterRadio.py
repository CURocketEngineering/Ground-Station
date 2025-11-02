from cure_ground.core.protocols.data_names.data_name_loader import load_data_name_enum

class TextFormatterRadio:
    def __init__(self, protocol_version: int = 3):
        # Load the data names YAML for the radio protocol
        self.data_names = load_data_name_enum(protocol_version)
        
        # Organize data by "category" for display purposes
        # For example: accelerometer, gyroscope, magnetometer, environment, telemetry
        self.categories = {
            'accelerometer': [],
            'gyroscope': [],
            'magnetometer': [],
            'environment': [],
            'telemetry': []
        }
        
        for item in self.data_names.data_definitions:
            name = item['name']
            # Assign keys to categories based on their name or type
            lname = name.lower()
            if 'accelerometer' in lname:
                self.categories['accelerometer'].append(name)
            elif 'gyroscope' in lname:
                self.categories['gyroscope'].append(name)
            elif 'magnetometer' in lname:
                self.categories['magnetometer'].append(name)
            elif lname in ['temperature', 'pressure', 'altitude']:
                self.categories['environment'].append(name)
            else:
                self.categories['telemetry'].append(name)
    
    def get_left_column_text(self, status_data):
        text_sections = []
        for cat in ['accelerometer', 'gyroscope', 'magnetometer', 'environment']:
            text_sections.append(self._format_category(cat, status_data))
        return "\n\n".join(text_sections)
    
    def get_right_column_text(self, status_data):
        return self._format_category('telemetry', status_data)
    
    def _format_category(self, category: str, status_data) -> str:
        lines = [f"--{category.capitalize()}--"]
        for key in self.categories.get(category, []):
            value = status_data.get(key, 'N/A')
            # Add units if desired; you could extend this with a unit mapping
            lines.append(f"{key}: {value}")
        return "\n".join(lines)

class TextFormatterCSV:
    def get_left_column_text(self, status_data):
        return (
            self.get_accelerometer_text(status_data)
            + "\n\n"
            + self.get_gyroscope_text(status_data)
            + "\n\n"
            + self.get_magnetometer_text(status_data)
            + "\n\n"
            + self.get_other_text(status_data)
        )

    def get_right_column_text(self, status_data):
        return self.get_sensors_text(status_data)

    def get_accelerometer_text(self, status_data):
        return f"""--Accelerometer--
Accelerometer X: {status_data.get("ACCELEROMETER_X", "N/A")}
Accelerometer Y: {status_data.get("ACCELEROMETER_Y", "N/A")}
Accelerometer Z: {status_data.get("ACCELEROMETER_Z", "N/A")}"""

    def get_gyroscope_text(self, status_data):
        return f"""--Apogee Detector--
Gyroscope X: {status_data.get("GYROSCOPE_X", "N/A")}
Gyroscope Y: {status_data.get("GYROSCOPE_Y", "N/A")}
Gyroscope Z: {status_data.get("GYROSCOPE_Z", "N/A")}"""

    def get_magnetometer_text(self, status_data):
        return f"""--Data Saver--
Magnetometer X: {status_data.get("MAGNETOMETER_X", "N/A")}
Magnetometer Y: {status_data.get("MAGNETOMETER_Y", "N/A")}
Magnetometer Z: {status_data.get("MAGNETOMETER_Z", "N/A")}"""

    def get_other_text(self, status_data):
        return f"""--Flash--
Temperature: {status_data.get("TEMPERATURE", "N/A")}
Pressure: {status_data.get("PRESSURE", "N/A")}
Altitude: {status_data.get("ALTITUDE", "N/A")}"""

    def get_sensors_text(self, status_data):
        return f"""--Sensors--
Median Acceleration Squared: {status_data.get("MEDIAN_ACCELERATION_SQUARED", "N/A")}
Average Cycle Rate: {status_data.get("AVERAGE_CYCLE_RATE", "N/A")}
Timestamp: {status_data.get("TIMESTAMP", "N/A")}
State Change: {status_data.get("STATE_CHANGE", "N/A")}
Flight ID: {status_data.get("FLIGHT_ID", "N/A")}
Estimated Apogee: {status_data.get("EST_APOGEE", "N/A")}
Estimated Vertical Velocity: {status_data.get("EST_VERTICAL_VELOCITY", "N/A")}
Estimated Altitude: {status_data.get("EST_ALTITUDE", "N/A")}
Battery Voltage: {status_data.get("BATTERY_VOLTAGE", "N/A")}
Fin Deployment Amount: {status_data.get("FIN_DEPLOYMENT_AMOUNT", "N/A")}
Time to Apogee: {status_data.get("TIME_TO_APOGEE", "N/A")}"""

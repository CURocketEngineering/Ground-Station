class TextFormatter:
    def get_left_column_text(self, status_data):
        return (
            self.get_launch_predictor_text(status_data)
            + "\n\n"
            + self.get_apogee_detector_text(status_data)
            + "\n\n"
            + self.get_data_saver_text(status_data)
            + "\n\n"
            + self.get_flash_text(status_data)
        )

    def get_right_column_text(self, status_data):
        return self.get_sensors_text(status_data)

    def get_launch_predictor_text(self, status_data):
        return f"""--Launch Predictor--
Launched: {status_data.get("launchPredictorLaunched", "N/A")}
Launched Time: {status_data.get("launchPredictorLaunchedTime", "N/A")}
Median Acceleration Squared: {status_data.get("launchPredictorMedianAccelerationSquared", "N/A")}"""

    def get_apogee_detector_text(self, status_data):
        return f"""--Apogee Detector--
Apogee Detected: {status_data.get("apogeeDetected", "N/A")}
Estimated Altitude: {status_data.get("estimatedAltitude", "N/A")}
Estimated Velocity: {status_data.get("estimatedVelocity", "N/A")}
Inertial Vertical Acceleration: {status_data.get("inertialVerticalAcceleration", "N/A")}
Vertical Axis: {status_data.get("verticalAxis", "N/A")}
Vertical Direction: {status_data.get("verticalDirection", "N/A")}
Apogee Altitude: {status_data.get("apogeeAltitude", "N/A")}"""

    def get_data_saver_text(self, status_data):
        return f"""--Data Saver--
Post Launch Mode: {status_data.get("postLaunchMode", "N/A")}
Rebooted in Post Launch Mode (won't save): {status_data.get("rebootedInPostLaunchMode", "N/A")}
Last Timestamp: {status_data.get("lastTimestamp", "N/A")}
Last Data Point Value: {status_data.get("lastDataPointValue", "N/A")}
Super Loop Average Hz: {status_data.get("superLoopAverageHz", "N/A")}"""

    def get_flash_text(self, status_data):
        return f"""--Flash--
Stopped writing b/c wrapped around to launch address: {status_data.get("chipFullDueToPostLaunchProtection", "N/A")}
Launch Write Address: {status_data.get("launchWriteAddress", "N/A")}
Next Write Address: {status_data.get("nextWriteAddress", "N/A")}
Buffer Index: {status_data.get("bufferIndex", "N/A")}
Buffer Flushes: {status_data.get("bufferFlushes", "N/A")}"""

    def get_sensors_text(self, status_data):
        return f"""--Sensors--
Accelerometer X: {status_data.get("aclx", "N/A")}
Accelerometer Y: {status_data.get("acly", "N/A")}
Accelerometer Z: {status_data.get("aclz", "N/A")}
Gyroscope X: {status_data.get("gyrox", "N/A")}
Gyroscope Y: {status_data.get("gyroy", "N/A")}
Gyroscope Z: {status_data.get("gyroz", "N/A")}
Magnetometer X: {status_data.get("magx", "N/A")}
Magnetometer Y: {status_data.get("magy", "N/A")}
Magnetometer Z: {status_data.get("magz", "N/A")}
Temperature: {status_data.get("temp", "N/A")}
Pressure: {status_data.get("pressure", "N/A")}
Altitude: {status_data.get("alt", "N/A")}"""

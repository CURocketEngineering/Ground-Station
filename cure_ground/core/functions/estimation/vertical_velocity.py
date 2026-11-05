"""Vertical velocity estimates from recorded flight data."""

import numpy as np
import pandas as pd


def calculate_vertical_velocity(timestamps, altitudes):
    """Estimate vertical velocity (m/s) from altitude (m) and time (s).

    Samples must have strictly increasing timestamps. Use
    add_vertical_velocity() for Ground Station CSV data, which may have
    multiple rows for the same timestamp.
    """
    times = _values(timestamps, "timestamps")
    heights = _values(altitudes, "altitudes")
    _check_times(times, len(heights))

    return np.gradient(heights, times)


def fuse_vertical_velocity(
    timestamps,
    altitudes,
    vertical_acceleration,
    *,
    altitude_std=1.0,
    acceleration_std=1.0,
    initial_velocity=None,
):
    """Estimate velocity using altitude and gravity-corrected vertical acceleration.

    All measurements must be aligned and use seconds, meters, and m/s².
    Acceleration must already be transformed into the vertical axis, with
    gravity removed. Raw accelerometer X/Y/Z values are not valid inputs.

    The filter predicts height and velocity from acceleration, then corrects
    both using measured altitude. Noise parameters are standard deviations.
    """
    times = _values(timestamps, "timestamps")
    heights = _values(altitudes, "altitudes")
    acceleration = _values(vertical_acceleration, "vertical_acceleration")
    _check_times(times, len(heights))

    if len(acceleration) != len(times):
        raise ValueError("Acceleration and timestamps must have equal lengths.")
    if not np.isfinite(altitude_std) or altitude_std <= 0:
        raise ValueError("altitude_std must be positive and finite.")
    if not np.isfinite(acceleration_std) or acceleration_std <= 0:
        raise ValueError("acceleration_std must be positive and finite.")

    intervals = np.diff(times)
    if initial_velocity is None:
        # The first two altitude samples provide the initial velocity estimate.
        first_acceleration = (acceleration[0] + acceleration[1]) / 2
        velocity = (heights[1] - heights[0]) / intervals[0]
        velocity -= 0.5 * first_acceleration * intervals[0]
    else:
        velocity = float(initial_velocity)
        if not np.isfinite(velocity):
            raise ValueError("initial_velocity must be finite.")

    altitude = heights[0]
    altitude_var = float(altitude_std) ** 2
    acceleration_var = float(acceleration_std) ** 2
    height_var = altitude_var
    cross_var = 0.0
    velocity_var = 2 * altitude_var / intervals[0] ** 2

    velocities = np.empty(len(times), dtype=float)
    velocities[0] = velocity

    for i, dt in enumerate(intervals, start=1):
        a = (acceleration[i - 1] + acceleration[i]) / 2
        predicted_altitude = altitude + velocity * dt + 0.5 * a * dt**2
        predicted_velocity = velocity + a * dt

        predicted_height_var = (
            height_var + 2 * dt * cross_var + dt**2 * velocity_var
            + 0.25 * dt**4 * acceleration_var
        )
        predicted_cross_var = (
            cross_var + dt * velocity_var + 0.5 * dt**3 * acceleration_var
        )
        predicted_velocity_var = velocity_var + dt**2 * acceleration_var

        residual = heights[i] - predicted_altitude
        residual_var = predicted_height_var + altitude_var
        height_gain = predicted_height_var / residual_var
        velocity_gain = predicted_cross_var / residual_var

        altitude = predicted_altitude + height_gain * residual
        velocity = predicted_velocity + velocity_gain * residual

        height_var = (1 - height_gain) * predicted_height_var
        cross_var = (1 - height_gain) * predicted_cross_var
        velocity_var = predicted_velocity_var - velocity_gain * predicted_cross_var
        velocities[i] = velocity

    return velocities


def add_vertical_velocity(
    recording,
    *,
    vertical_acceleration_column=None,
    output_column="CALCULATED_VERTICAL_VELOCITY",
):
    """Add a velocity column to a Ground Station recording DataFrame.

    TIMESTAMP is in milliseconds and ALTITUDE is in meters. Repeated
    timestamps use the last valid measurement at that time; each matching row
    receives the same calculated velocity. Rows without an altitude reading at
    their timestamp retain NaN, rather than receiving an invented value.

    An optional acceleration column must contain gravity-corrected vertical
    acceleration in m/s², not raw accelerometer axis measurements.
    """
    if not isinstance(recording, pd.DataFrame):
        raise TypeError("recording must be a pandas DataFrame.")

    columns = ["TIMESTAMP", "ALTITUDE"]
    if vertical_acceleration_column is not None:
        columns.append(vertical_acceleration_column)
    missing = [column for column in columns if column not in recording]
    if missing:
        raise ValueError(f"Missing recording columns: {', '.join(missing)}")
    if output_column in recording.columns:
        raise ValueError(f"Output column already exists: {output_column}")

    times_ms = pd.to_numeric(recording["TIMESTAMP"], errors="coerce")
    if not np.isfinite(times_ms.to_numpy(dtype=float)).all():
        raise ValueError("TIMESTAMP must contain only finite numeric values.")
    if np.any(np.diff(times_ms.to_numpy(dtype=float)) < 0):
        raise ValueError("TIMESTAMP values must be in chronological order.")

    data = pd.DataFrame({
        "timestamp": times_ms.to_numpy(dtype=float),
        "altitude": pd.to_numeric(recording["ALTITUDE"], errors="coerce").to_numpy(),
    })
    data["altitude"] = data["altitude"].where(np.isfinite(data["altitude"]))

    if vertical_acceleration_column is not None:
        data["acceleration"] = pd.to_numeric(
            recording[vertical_acceleration_column], errors="coerce"
        ).to_numpy()
        data["acceleration"] = data["acceleration"].where(
            np.isfinite(data["acceleration"])
        )

    # A recording may repeat timestamps as different sensor packets arrive.
    samples = data.groupby("timestamp", sort=True).last().dropna(subset=["altitude"])
    if len(samples) < 2:
        raise ValueError("Recording needs at least two distinct altitude timestamps.")

    seconds = (samples.index.to_numpy(dtype=float) - samples.index[0]) / 1000.0
    if vertical_acceleration_column is None:
        velocity = calculate_vertical_velocity(seconds, samples["altitude"])
    else:
        if samples["acceleration"].isna().any():
            raise ValueError("Vertical acceleration is missing at some altitude timestamps.")
        velocity = fuse_vertical_velocity(
            seconds, samples["altitude"], samples["acceleration"]
        )

    result = recording.copy()
    by_time = pd.Series(velocity, index=samples.index)
    result[output_column] = times_ms.map(by_time).to_numpy()
    return result


def _values(values, name):
    try:
        array = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must contain numeric values.") from error
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must contain only finite values.")
    return array


def _check_times(times, other_length):
    if len(times) != other_length:
        raise ValueError("Timestamps and altitudes must have equal lengths.")
    if len(times) < 2:
        raise ValueError("At least two measurements are required.")
    if np.any(np.diff(times) <= 0):
        raise ValueError("Timestamps must be strictly increasing.")

"""Tests for flight-data vertical velocity estimates."""

import numpy as np
import pandas as pd
import pytest

from cure_ground.core.functions.estimation.vertical_velocity import (
    add_vertical_velocity,
    calculate_vertical_velocity,
    fuse_vertical_velocity,
)


def test_constant_altitude():
    result = calculate_vertical_velocity([0, 1, 2, 3], [100, 100, 100, 100])
    np.testing.assert_allclose(result, [0, 0, 0, 0])


def test_ascending():
    result = calculate_vertical_velocity([0, 1, 2, 3], [0, 10, 20, 30])
    np.testing.assert_allclose(result, [10, 10, 10, 10])


def test_descending():
    result = calculate_vertical_velocity([0, 1, 2, 3], [30, 20, 10, 0])
    np.testing.assert_allclose(result, [-10, -10, -10, -10])


def test_uneven_timestamps():
    result = calculate_vertical_velocity([0, 1, 3], [0, 5, 15])
    np.testing.assert_allclose(result, [5, 5, 5])


def test_mismatched_lengths():
    with pytest.raises(ValueError):
        calculate_vertical_velocity([0, 1, 2], [0, 10])


def test_duplicate_timestamps():
    with pytest.raises(ValueError):
        calculate_vertical_velocity([0, 1, 1], [0, 10, 20])


def test_insufficient_measurements():
    with pytest.raises(ValueError):
        calculate_vertical_velocity([0], [10])


def test_invalid_values():
    with pytest.raises(ValueError):
        calculate_vertical_velocity([0, 1, 2], [0, np.nan, 20])


def test_constant_acceleration():
    times = np.arange(6, dtype=float)
    acceleration = np.full(6, 2.0)
    altitudes = times**2
    result = fuse_vertical_velocity(times, altitudes, acceleration)
    np.testing.assert_allclose(result, 2 * times, atol=1e-10)


def test_fusion_at_constant_speed():
    times = [0.0, 0.4, 1.0, 1.4]
    altitudes = [5 + 3 * t for t in times]
    result = fuse_vertical_velocity(times, altitudes, [0, 0, 0, 0])
    np.testing.assert_allclose(result, [3, 3, 3, 3], atol=1e-10)


def test_fusion_rejects_unaligned_acceleration():
    with pytest.raises(ValueError, match="equal lengths"):
        fuse_vertical_velocity([0, 1, 2], [0, 1, 2], [0, 1])


def test_fusion_rejects_invalid_noise():
    with pytest.raises(ValueError, match="altitude_std"):
        fuse_vertical_velocity([0, 1], [0, 1], [0, 0], altitude_std=0)


def test_csv_duplicate_timestamps():
    data = pd.DataFrame({
        "TIMESTAMP": [1000, 1000, 2000, 2000, 3000],
        "ALTITUDE": [0, 0, 10, 10, 20],
    })
    result = add_vertical_velocity(data)
    np.testing.assert_allclose(result["CALCULATED_VERTICAL_VELOCITY"], [10] * 5)
    assert "CALCULATED_VERTICAL_VELOCITY" not in data.columns


def test_csv_last_valid_measurement():
    data = pd.DataFrame({
        "TIMESTAMP": [0, 0, 1000, 1000, 2000],
        "ALTITUDE": [0, np.nan, 10, np.nan, 20],
    })
    result = add_vertical_velocity(data)
    np.testing.assert_allclose(result["CALCULATED_VERTICAL_VELOCITY"], [10] * 5)


def test_csv_missing_altitude_keeps_nan():
    data = pd.DataFrame({
        "TIMESTAMP": [0, 1000, 2000, 3000],
        "ALTITUDE": [0, np.nan, 20, 30],
    })
    result = add_vertical_velocity(data)
    assert np.isnan(result["CALCULATED_VERTICAL_VELOCITY"].iloc[1])
    np.testing.assert_allclose(
        result["CALCULATED_VERTICAL_VELOCITY"].iloc[[0, 2, 3]], [10, 10, 10]
    )


def test_csv_rejects_backward_time():
    data = pd.DataFrame({"TIMESTAMP": [1000, 0], "ALTITUDE": [0, 1]})
    with pytest.raises(ValueError, match="chronological"):
        add_vertical_velocity(data)


def test_csv_fusion_with_corrected_acceleration():
    data = pd.DataFrame({
        "TIMESTAMP": [0, 1000, 2000, 3000],
        "ALTITUDE": [0, 1, 4, 9],
        "VERTICAL_ACCELERATION": [2, 2, 2, 2],
    })
    result = add_vertical_velocity(data, vertical_acceleration_column="VERTICAL_ACCELERATION")
    np.testing.assert_allclose(result["CALCULATED_VERTICAL_VELOCITY"], [0, 2, 4, 6], atol=1e-10)


def test_csv_fusion_missing_acceleration():
    data = pd.DataFrame({
        "TIMESTAMP": [0, 1000], "ALTITUDE": [0, 1],
        "VERTICAL_ACCELERATION": [0, np.nan],
    })
    with pytest.raises(ValueError, match="acceleration is missing"):
        add_vertical_velocity(data, vertical_acceleration_column="VERTICAL_ACCELERATION")

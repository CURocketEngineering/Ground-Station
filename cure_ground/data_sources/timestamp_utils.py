import math
from statistics import median
from typing import Iterable, Optional


TIMESTAMP_KEYS = ("TIMESTAMP", "timestamp", "Timestamp")

# Approximate thresholds to distinguish unix epoch units.
EPOCH_SECONDS_LOWER_BOUND = 1_000_000_000
EPOCH_MILLISECONDS_LOWER_BOUND = 100_000_000_000
FRACTIONAL_TOLERANCE = 1e-6


def parse_timestamp_value(value: object) -> Optional[float]:
    if value in (None, "", "N/A"):
        return None

    try:
        timestamp = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(timestamp):
        return None

    return timestamp


def infer_timestamp_multiplier_to_ms(values: Iterable[float]) -> int:
    timestamps = []
    for value in values:
        parsed = parse_timestamp_value(value)
        if parsed is not None:
            timestamps.append(parsed)

    if not timestamps:
        return 1

    max_abs_timestamp = max(abs(timestamp) for timestamp in timestamps)
    if max_abs_timestamp >= EPOCH_MILLISECONDS_LOWER_BOUND:
        return 1

    if max_abs_timestamp >= EPOCH_SECONDS_LOWER_BOUND:
        return 1000

    has_fractional_values = any(
        abs(timestamp - round(timestamp)) > FRACTIONAL_TOLERANCE
        for timestamp in timestamps
    )
    if has_fractional_values:
        return 1000

    positive_deltas = []
    for previous_timestamp, current_timestamp in zip(timestamps, timestamps[1:]):
        delta = current_timestamp - previous_timestamp
        if delta > 0:
            positive_deltas.append(delta)

    if positive_deltas and median(positive_deltas) < 1.0:
        return 1000

    return 1


def to_milliseconds(value: float, multiplier_to_ms: int) -> int:
    return int(round(value * multiplier_to_ms))

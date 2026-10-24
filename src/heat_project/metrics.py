"""Temperature error and threshold-time metrics with explicit missing results."""

import numpy as np
from numpy.typing import ArrayLike

from .model import _finite_real


def temperature_errors(numerical: ArrayLike, reference: ArrayLike) -> dict[str, float]:
    """Compute errors against an independently evaluated temperature field.

    Parameters
    ----------
    numerical, reference : array_like
        Finite temperature arrays in degrees Celsius, with identical nonempty
        shapes. Spatial boundary values are included if supplied.

    Returns
    -------
    dict
        ``rmse_c`` and ``max_abs_error_c``, both in degrees Celsius.

    Raises
    ------
    ValueError
        If shapes differ, arrays are empty, or inputs are non-finite.
    """
    actual, expected = np.asarray(numerical, dtype=float), np.asarray(reference, dtype=float)
    if actual.shape != expected.shape or actual.size == 0:
        raise ValueError("temperature arrays must have identical nonempty shapes")
    if not np.all(np.isfinite(actual)) or not np.all(np.isfinite(expected)):
        raise ValueError("temperature arrays must contain only finite values")
    absolute = np.abs(actual - expected)
    maximum = float(np.max(absolute))
    # Scale first to avoid squaring overflow on large but finite errors.
    rmse = 0.0 if maximum == 0 else maximum * float(np.sqrt(np.mean((absolute/maximum)**2)))
    return {"rmse_c": rmse, "max_abs_error_c": maximum}


def threshold_crossing_time(times_s: ArrayLike, max_temperature_c: ArrayLike,
                            target_temp_c: float) -> float | None:
    """Find the first at-or-below-target sample and interpolate its crossing.

    Parameters
    ----------
    times_s : array_like, shape (M,)
        Finite, nonnegative, strictly increasing sample times, in seconds.
    max_temperature_c : array_like, shape (M,)
        Finite sampled spatial maximum temperatures, in degrees Celsius.
        Monotonic cooling is not assumed; the first downward crossing is used.
    target_temp_c : float
        Finite threshold in degrees Celsius.

    Returns
    -------
    float or None
        First crossing time, in seconds, linearly interpolated between adjacent
        samples. Return the first time if the initial value is already at or
        below target; return ``None`` if the target was never reached.

    Raises
    ------
    ValueError
        For unequal or invalid histories, non-increasing/negative times or a
        non-finite threshold.
    """
    _finite_real("target_temp_c", target_temp_c)
    times = np.asarray(times_s, dtype=float)
    temperatures = np.asarray(max_temperature_c, dtype=float)
    if (times.ndim != 1 or temperatures.ndim != 1 or times.shape != temperatures.shape
            or times.size == 0):
        raise ValueError("histories must be nonempty one-dimensional arrays with identical shapes")
    if not np.all(np.isfinite(times)) or not np.all(np.isfinite(temperatures)):
        raise ValueError("histories must contain only finite values")
    if np.any(times < 0) or np.any(np.diff(times) <= 0):
        raise ValueError("times must be nonnegative and strictly increasing")
    hits = np.flatnonzero(temperatures <= target_temp_c)
    if not len(hits):
        return None
    index = int(hits[0])
    if index == 0:
        return float(times[0])
    fraction = ((temperatures[index-1] - target_temp_c)
                / (temperatures[index-1] - temperatures[index]))
    return float(times[index-1] + fraction*(times[index]-times[index-1]))

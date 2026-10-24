"""Analytical slab solutions, independent of the finite-difference solvers."""

import math
from numbers import Integral

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import brentq
from scipy.special import exp1

from .model import PlateConfig, _finite_real


def _coordinates(x_m: ArrayLike, time_s: float,
                 plate: PlateConfig) -> NDArray[np.float64]:
    """Validate evaluation coordinates and a nonnegative scalar time."""
    plate.validate()
    _finite_real("time_s", time_s)
    if time_s < 0:
        raise ValueError("time_s must be nonnegative")
    x = np.asarray(x_m, dtype=float)
    if not np.all(np.isfinite(x)) or np.any(x < 0) or np.any(x > plate.length_m):
        raise ValueError("x_m must contain finite positions between 0 and length_m")
    return x


def sine_temperature(x_m: ArrayLike, time_s: float, plate: PlateConfig,
                     amplitude_c: float = 80.0) -> NDArray[np.float64]:
    """Evaluate the exact smooth single-sine heat-equation solution.

    Parameters
    ----------
    x_m : array_like
        Positions in metres, within ``[0, length_m]``.
    time_s : float
        Nonnegative time in seconds.
    plate : PlateConfig
        Slab thickness, diffusivity and boundary temperature.
    amplitude_c : float
        Finite initial sine amplitude, in degrees Celsius.

    Returns
    -------
    ndarray
        Temperature in degrees Celsius, with the same shape as ``x_m``.

    Raises
    ------
    ValueError
        For invalid coordinates, time or amplitude.
    """
    x = _coordinates(x_m, time_s, plate)
    _finite_real("amplitude_c", amplitude_c)
    decay = np.exp(-plate.diffusivity_m2_s * (np.pi/plate.length_m)**2 * time_s)
    temperature = plate.boundary_temp_c + amplitude_c*np.sin(np.pi*x/plate.length_m)*decay
    return np.where((x == 0) | (x == plate.length_m), plate.boundary_temp_c, temperature)


def uniform_temperature(x_m: ArrayLike, time_s: float, plate: PlateConfig,
                        terms: int = 200) -> NDArray[np.float64]:
    """Evaluate a converged odd-sine series for uniform initial slab cooling.

    Parameters
    ----------
    x_m : array_like
        Positions in metres, within ``[0, length_m]``.
    time_s : float
        Nonnegative time, in seconds. At exactly zero, return the prescribed
        uniform interior initial temperature and the imposed face values.
    plate : PlateConfig
        Physical inputs; the full thickness is used in every eigenvalue.
    terms : int
        Positive starting number of odd Fourier terms. It is doubled if an
        absolute tail bound is above 1e-11 degrees Celsius. At most 131072
        terms are used; times too close to zero can exceed this limit.

    Returns
    -------
    ndarray
        Temperature in degrees Celsius, with the same shape as ``x_m``.

    Raises
    ------
    ValueError
        For invalid inputs or if a positive evaluation time is too close to
        zero to satisfy the series truncation bound within the term limit.

    Notes
    -----
    For ``a = alpha*(pi/L)**2*t`` and first omitted odd index ``q=2*K+1``,
    the absolute omitted series is bounded by
    ``4*abs(delta_T)/pi * (exp(-a*q*q)/q + exp1(a*q*q)/4)``.
    This follows from a decreasing-term integral bound and does not depend
    on fortuitous cancellation at particular spatial positions. The check
    bounds series truncation, not machine round-off or physical model error.
    """
    x = _coordinates(x_m, time_s, plate)
    if isinstance(terms, bool) or not isinstance(terms, Integral) or terms < 1:
        raise ValueError("terms must be a positive integer")
    if terms > 131072:
        raise ValueError("terms must not exceed 131072")
    boundary = (x == 0) | (x == plate.length_m)
    if time_s == 0:
        return np.where(boundary, plate.boundary_temp_c, plate.initial_temp_c)
    delta = plate.initial_temp_c - plate.boundary_temp_c
    if delta == 0:
        return np.full_like(x, plate.boundary_temp_c)
    a = plate.diffusivity_m2_s * (np.pi/plate.length_m)**2 * time_s
    k = int(terms)
    while True:
        q = 2*k + 1
        tail = 4*abs(delta)/np.pi * (np.exp(-a*q*q)/q + exp1(a*q*q)/4)
        if tail <= 1e-11:
            break
        if k >= 131072:
            raise ValueError("positive time is too close to zero for the series convergence limit")
        k = min(2*k, 131072)
    # Chunking bounds temporary storage even when an early time needs many
    # modes; there is no dense mode-by-position history to retain.
    total = np.zeros_like(x)
    for start in range(0, k, 512):
        odd = 2*np.arange(start, min(start+512, k), dtype=float) + 1
        coefficients = np.exp(-a*odd**2)/odd
        values = np.sin(odd[:, None] * np.pi * x.reshape(1, -1)/plate.length_m)
        total += (coefficients @ values).reshape(x.shape)
    result = plate.boundary_temp_c + delta*4/np.pi*total
    return np.where(boundary, plate.boundary_temp_c, result)


def reference_temperature(x_m: ArrayLike, time_s: float, plate: PlateConfig,
                          profile: str = "uniform", amplitude_c: float = 80.0,
                          terms: int = 200) -> NDArray[np.float64]:
    """Select the uniform or sine analytical temperature reference.

    Parameters
    ----------
    x_m : array_like
        Spatial coordinates in metres.
    time_s : float
        Evaluation time in seconds, nonnegative.
    plate : PlateConfig
        Physical inputs.
    profile : {'uniform', 'sine'}
        Reference initial condition.
    amplitude_c : float
        Sine amplitude in degrees Celsius, used for the sine profile only.
    terms : int
        Starting odd-term count, used for the uniform profile only.

    Returns
    -------
    ndarray
        Analytical temperatures in degrees Celsius, shaped like ``x_m``.

    Raises
    ------
    ValueError
        For unsupported profiles or invalid reference inputs.
    """
    if profile == "uniform":
        return uniform_temperature(x_m, time_s, plate, terms=terms)
    if profile == "sine":
        return sine_temperature(x_m, time_s, plate, amplitude_c=amplitude_c)
    raise ValueError("profile must be 'uniform' or 'sine'")


def reference_cooling_time(plate: PlateConfig) -> float:
    """Find when the hottest point of a uniformly heated slab reaches target.

    Parameters
    ----------
    plate : PlateConfig
        Physical inputs satisfying ``boundary_temp_c < target_temp_c <
        initial_temp_c``. The hottest point is the symmetric slab centre.

    Returns
    -------
    float
        Threshold time in seconds from a bracketed root of the converged
        analytical series, independently of numerical solver step sizes.

    Raises
    ------
    ValueError
        If the target is outside the strict cooling interval or the derived
        characteristic time cannot be represented as a finite float.
    """
    plate.validate()
    if not plate.boundary_temp_c < plate.target_temp_c < plate.initial_temp_c:
        raise ValueError("cooling reference requires boundary_temp_c < target_temp_c < initial_temp_c")
    characteristic = plate.length_m**2 / plate.diffusivity_m2_s
    if not math.isfinite(characteristic) or characteristic <= 0:
        raise ValueError("the characteristic cooling time is not numerically representable")

    def residual(fourier_number: float) -> float:
        return float(uniform_temperature(plate.length_m/2,
                                         fourier_number*characteristic, plate)
                     - plate.target_temp_c)

    high = 1.0
    while residual(high) > 0:
        high *= 2
    fourier_number = brentq(residual, 0.0, high, xtol=1e-13, rtol=1e-12)
    return float(fourier_number * characteristic)

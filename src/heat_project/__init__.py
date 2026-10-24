"""Verified finite-difference tools for idealised one-dimensional slab cooling.

The package separates input contracts, numerical integration, independent
analytical references and error metrics. Temperatures use degrees Celsius,
positions metres and times seconds. Analytical agreement verifies the stated
mathematical model; it does not constitute experimental physical validation.
"""

from .model import PlateConfig, SolverConfig
from .solvers import SimulationResult, solve
from .reference import (
    reference_cooling_time,
    reference_temperature,
    sine_temperature,
    uniform_temperature,
)
from .metrics import temperature_errors, threshold_crossing_time

__all__ = [
    "PlateConfig", "SolverConfig", "SimulationResult", "solve",
    "sine_temperature", "uniform_temperature", "reference_temperature",
    "reference_cooling_time", "temperature_errors", "threshold_crossing_time",
]

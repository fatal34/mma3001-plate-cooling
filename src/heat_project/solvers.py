"""FTCS and banded backward Euler solvers with sparse field snapshots."""

from dataclasses import dataclass
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import solve_banded

from .model import PlateConfig, SolverConfig


@dataclass(frozen=True)
class SimulationResult:
    """Outputs from :func:`solve`, with temperatures in degrees Celsius.

    Attributes
    ----------
    x_m : ndarray, shape (N+1,)
        Spatial coordinates, in metres.
    times_s, max_temperature_c : ndarray, shape (M+1,)
        Every integration time and the spatial maximum at that time. The
        initial state is included. Time intervals may vary at snapshots.
    temperature_snapshots_c : ndarray, shape (S, N+1)
        Full spatial fields at requested snapshot times only.
    snapshot_times_s : ndarray, shape (S,)
        Sorted unique snapshot times, in seconds.
    final_temperature_c : ndarray, shape (N+1,)
        Full field at the exact requested endpoint, in degrees Celsius.
    steps : int
        Actual number of integration steps, M.
    dt_max_s : float
        Largest actual integration step, in seconds.
    diffusion_number : float
        Largest actual ``alpha*dt/dx**2`` used, including shortened steps.
    method : str
        Name of the numerical method.
    """

    x_m: NDArray[np.float64]
    times_s: NDArray[np.float64]
    max_temperature_c: NDArray[np.float64]
    temperature_snapshots_c: NDArray[np.float64]
    snapshot_times_s: NDArray[np.float64]
    final_temperature_c: NDArray[np.float64]
    steps: int
    dt_max_s: float
    diffusion_number: float
    method: str


def _snapshot_schedule(snapshot_times: Sequence[float] | None,
                       end_time_s: float) -> NDArray[np.float64]:
    """Return finite, sorted unique times without silently clipping inputs."""
    if snapshot_times is None:
        # Default output must not silently divide a deliberately large step.
        # Additional requested snapshot events can shorten integration steps.
        return np.array([0.0, end_time_s])
    try:
        requested = np.asarray(snapshot_times, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("snapshot_times must be a one-dimensional finite sequence") from exc
    if requested.ndim != 1 or not np.all(np.isfinite(requested)):
        raise ValueError("snapshot_times must be a one-dimensional finite sequence")
    if np.any(requested < 0) or np.any(requested > end_time_s):
        raise ValueError("snapshot times must lie between 0 and end_time_s")
    return np.unique(requested)


def solve(plate: PlateConfig, settings: SolverConfig,
          snapshot_times: Sequence[float] | None = None) -> SimulationResult:
    """Integrate the slab heat equation with fixed equal face temperatures.

    Parameters
    ----------
    plate : PlateConfig
        Physical inputs, with thickness in metres and diffusivity in m²/s.
    settings : SolverConfig
        Valid grid, integration and initial-condition controls.
    snapshot_times : sequence of float, optional
        Exact times in seconds at which to retain the full field, within
        ``[0, end_time_s]``. Times are sorted and deduplicated. The default
        retains the initial and final states without inserting extra internal
        events. An empty sequence retains no snapshots. The final field is
        always returned separately.

    Returns
    -------
    SimulationResult
        Fields at the requested times plus a maximum-temperature history for
        every time step. Array dimensions are documented in the result class.

    Raises
    ------
    ValueError
        For invalid inputs, snapshot times or an unstable normal FTCS setting.
    FloatingPointError
        If a diagnostic diverges to non-finite temperatures or a requested
        step cannot advance floating-point time. Unstable finite temperatures
        are returned without clipping.

    Notes
    -----
    Both solvers use O(N) working field storage; the scalar maximum history
    uses O(M), and requested snapshots use O(SN). FTCS updates every interior
    point from the old state. Backward Euler solves the tridiagonal system
    with known boundary contributions added to its right-hand side.

    Examples
    --------
    >>> result = solve(PlateConfig(), SolverConfig(end_time_s=0.01))
    >>> result.final_temperature_c.shape
    (81,)
    """
    if not isinstance(plate, PlateConfig) or not isinstance(settings, SolverConfig):
        raise ValueError("plate and settings must be PlateConfig and SolverConfig")
    settings.validate(plate)
    requested = _snapshot_schedule(snapshot_times, settings.end_time_s)
    n = int(settings.intervals)
    x = np.linspace(0.0, plate.length_m, n + 1)
    dx = plate.length_m / n
    rate = plate.diffusivity_m2_s / dx**2
    if settings.profile == "uniform":
        field = np.full(n + 1, plate.initial_temp_c, dtype=float)
    else:
        field = (plate.boundary_temp_c
                 + settings.amplitude_c * np.sin(np.pi * x / plate.length_m))
    if settings.perturbation_c:
        field[1:-1] += settings.perturbation_c * (-1.0)**np.arange(1, n)
    field[[0, -1]] = plate.boundary_temp_c
    if not np.all(np.isfinite(field)):
        raise ValueError("initial temperature calculation produced non-finite values")

    times = [0.0]
    maxima = [float(np.max(field))]
    snapshots: list[NDArray[np.float64]] = []
    snapshot_index = 0
    if len(requested) and requested[0] == 0.0:
        snapshots.append(field.copy())
        snapshot_index = 1

    t = 0.0
    max_dt = 0.0
    segment_start = 0.0
    segment_step = 1
    # Cache only the most recent step's matrix; a shortened snapshot step
    # changes r, so it must not reuse an incompatible matrix.
    previous_r = None
    banded = None
    while t < settings.end_time_s:
        stop = settings.end_time_s
        if snapshot_index < len(requested):
            stop = float(requested[snapshot_index])
        # Anchor each segment to its event start rather than repeatedly adding
        # dt. This avoids cumulative drift and spurious microscopic end steps.
        candidate = segment_start + segment_step * settings.dt_s
        tolerance = 8 * np.finfo(float).eps * max(abs(stop), abs(candidate))
        if candidate >= stop - tolerance:
            next_t = stop
        else:
            next_t = candidate
        dt = next_t - t
        if dt <= 0 or not np.isfinite(dt):
            raise FloatingPointError("time step cannot advance floating-point time")
        r = rate * dt
        with np.errstate(over="ignore", invalid="ignore"):
            if settings.method == "ftcs":
                updated = field.copy()
                if settings.implementation == "vectorized":
                    updated[1:-1] = (field[1:-1] + r
                                     * (field[:-2] - 2 * field[1:-1] + field[2:]))
                else:
                    for i in range(1, n):
                        updated[i] = field[i] + r * (field[i-1] - 2*field[i] + field[i+1])
            else:
                if previous_r != r:
                    banded = np.zeros((3, n - 1))
                    banded[0, 1:] = -r
                    banded[1, :] = 1 + 2*r
                    banded[2, :-1] = -r
                    previous_r = r
                rhs = field[1:-1].copy()
                rhs[0] += r * plate.boundary_temp_c
                rhs[-1] += r * plate.boundary_temp_c
                updated = field.copy()
                updated[1:-1] = solve_banded((1, 1), banded, rhs, check_finite=False)
        if not np.all(np.isfinite(updated)):
            raise FloatingPointError("non-finite temperature: diagnostic integration diverged")
        field = updated
        t = next_t
        times.append(t)
        maxima.append(float(np.max(field)))
        max_dt = max(max_dt, dt)
        if snapshot_index < len(requested) and t == requested[snapshot_index]:
            snapshots.append(field.copy())
            snapshot_index += 1
        if t == stop:
            segment_start = t
            segment_step = 1
        else:
            segment_step += 1

    stored = np.stack(snapshots) if snapshots else np.empty((0, n + 1), dtype=float)
    return SimulationResult(
        x_m=x, times_s=np.asarray(times), max_temperature_c=np.asarray(maxima),
        temperature_snapshots_c=stored, snapshot_times_s=requested,
        final_temperature_c=field.copy(), steps=len(times)-1, dt_max_s=max_dt,
        diffusion_number=rate*max_dt, method=settings.method,
    )

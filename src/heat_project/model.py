"""Validated physical and numerical inputs for one-dimensional heat diffusion."""

from dataclasses import dataclass
import math
from numbers import Integral, Real


def _finite_real(name: str, value: float, *, positive: bool = False) -> None:
    """Reject booleans, non-scalars and non-finite values with a clear message."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real scalar")
    if not math.isfinite(value) or (positive and value <= 0):
        qualifier = "positive finite" if positive else "finite"
        raise ValueError(f"{name} must be {qualifier}")


@dataclass(frozen=True)
class PlateConfig:
    """Physical inputs for a homogeneous slab with equal fixed face temperatures.

    Parameters
    ----------
    length_m : float
        Full slab thickness, in metres; must be positive and finite.
    diffusivity_m2_s : float
        Constant thermal diffusivity, in square metres per second; positive.
    initial_temp_c, boundary_temp_c, target_temp_c : float
        Finite temperatures in degrees Celsius. The mathematical solver also
        supports equal temperatures and heating cases. The cooling-time
        reference additionally requires ``boundary < target < initial``.

    Raises
    ------
    ValueError
        If physical inputs are non-finite or geometry/diffusivity is not positive.
    """

    length_m: float = 0.01
    diffusivity_m2_s: float = 1e-5
    initial_temp_c: float = 100.0
    boundary_temp_c: float = 20.0
    target_temp_c: float = 40.0

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate units-independent scalar domains; raise ``ValueError``."""
        _finite_real("length_m", self.length_m, positive=True)
        _finite_real("diffusivity_m2_s", self.diffusivity_m2_s, positive=True)
        for name in ("initial_temp_c", "boundary_temp_c", "target_temp_c"):
            _finite_real(name, getattr(self, name))


@dataclass(frozen=True)
class SolverConfig:
    """Grid, time integration and initial-condition controls.

    Parameters
    ----------
    intervals : int
        Number of equal spatial intervals, at least 4; there are N+1 nodes.
    dt_s, end_time_s : float
        Requested maximum time step and simulation horizon, in seconds.
        Snapshot times and the endpoint can shorten individual steps.
    method : {'ftcs', 'backward_euler'}
        Explicit central-space update or implicit first-order Euler method.
    profile : {'uniform', 'sine'}
        Uniform interior initial temperature or a smooth sine benchmark.
    amplitude_c : float
        Finite sine amplitude in degrees Celsius, including zero or negative
        values for mathematical verification. Used only with ``profile='sine'``.
    implementation : {'vectorized', 'loop'}
        FTCS spatial update implementation. Backward Euler uses a banded solve
        for either value, so this choice affects FTCS only.
    allow_unstable : bool
        Permit FTCS diffusion number above 0.5 for a labelled diagnostic run.
    perturbation_c : float
        Finite alternating perturbation amplitude, in degrees Celsius, added
        to interior initial values to excite high-frequency numerical modes.

    Raises
    ------
    ValueError
        For unsupported options or invalid scalar inputs, or when
        ``validate(plate)`` detects an unstable normal FTCS setting.
    """

    intervals: int = 80
    dt_s: float = 0.0005
    end_time_s: float = 3.0
    method: str = "ftcs"
    profile: str = "uniform"
    amplitude_c: float = 80.0
    implementation: str = "vectorized"
    allow_unstable: bool = False
    perturbation_c: float = 0.0

    def __post_init__(self) -> None:
        self.validate()

    def validate(self, plate: PlateConfig | None = None) -> None:
        """Check scalar controls and, optionally, the FTCS stability restriction.

        Parameters
        ----------
        plate : PlateConfig, optional
            Physical inputs needed to evaluate ``alpha*dt/dx**2``. Validation
            uses ``min(dt_s, end_time_s)`` before snapshot splitting, making
            the normal-run stability check conservative.

        Raises
        ------
        ValueError
            If any control is invalid, the grid is unrepresentable, or the
            normal FTCS diffusion number exceeds 0.5.
        """
        if (isinstance(self.intervals, bool)
                or not isinstance(self.intervals, Integral)
                or self.intervals < 4):
            raise ValueError("intervals must be an integer >= 4")
        _finite_real("dt_s", self.dt_s, positive=True)
        _finite_real("end_time_s", self.end_time_s, positive=True)
        _finite_real("amplitude_c", self.amplitude_c)
        _finite_real("perturbation_c", self.perturbation_c)
        if self.method not in ("ftcs", "backward_euler"):
            raise ValueError("method must be 'ftcs' or 'backward_euler'")
        if self.profile not in ("uniform", "sine"):
            raise ValueError("profile must be 'uniform' or 'sine'")
        if self.implementation not in ("vectorized", "loop"):
            raise ValueError("implementation must be 'vectorized' or 'loop'")
        if not isinstance(self.allow_unstable, bool):
            raise ValueError("allow_unstable must be a bool")
        if plate is not None:
            plate.validate()
            dx = plate.length_m / self.intervals
            try:
                rate = plate.diffusivity_m2_s / dx**2
                diffusion_number = rate * min(self.dt_s, self.end_time_s)
            except (OverflowError, ZeroDivisionError) as exc:
                raise ValueError("geometry/time scales are not numerically representable") from exc
            if not math.isfinite(rate) or not math.isfinite(diffusion_number):
                raise ValueError("geometry/time scales are not numerically representable")
            if (self.method == "ftcs" and not self.allow_unstable
                    and diffusion_number > 0.5 + 16 * math.ulp(0.5)):
                raise ValueError(
                    f"FTCS requires diffusion number r <= 0.5; got {diffusion_number:.6g}. "
                    "Reduce dt_s or explicitly set allow_unstable=True for diagnostics."
                )

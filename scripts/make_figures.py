"""Regenerate publication-size figures from the saved experiment CSV tables.

Run ``python scripts/make_figures.py`` from any working directory. No numerical
experiments are rerun here: every plotted point comes from ``results/tables``.
Both vector PDF and 190 dpi PNG versions are written to ``results/figures``.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import tempfile

# Keep font-cache creation compatible with restricted desktop workspaces.
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "mma3001-mpl-cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
NAVY = "#17324D"
TEAL = "#007F83"
ORANGE = "#C86723"
GREY = "#7B8792"
COLOURS = {"ftcs": TEAL, "backward_euler": ORANGE}
LABELS = {"ftcs": "FTCS", "backward_euler": "Backward Euler"}


def read_table(filename: str) -> list[dict[str, str]]:
    """Read an experiment CSV without adding a dataframe dependency."""
    with (TABLES / filename).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def values(rows: list[dict[str, str]], key: str) -> np.ndarray:
    """Return a numerical CSV column, accepting blank missing values as NaN."""
    return np.array([float(row[key]) if row[key] else np.nan for row in rows])


def methods(rows: list[dict[str, str]]) -> list[str]:
    """Use the same method ordering in every figure."""
    return [method for method in ("ftcs", "backward_euler")
            if any(row["method"] == method for row in rows)]


def finish(fig: plt.Figure, name: str) -> None:
    """Save identical tight-layout PNG and PDF views, then release the figure."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=1.0, w_pad=2.1)
    fig.savefig(FIGURES / f"{name}.png", dpi=190, bbox_inches="tight", facecolor="white")
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def format_axes(ax: plt.Axes) -> None:
    """Keep scientific axes legible at report width without a heavy grid."""
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GREY)
    ax.tick_params(color=GREY, labelcolor=NAVY, direction="out", length=3)
    ax.xaxis.label.set_color(NAVY)
    ax.yaxis.label.set_color(NAVY)


def temperature_profiles() -> None:
    """Plot field profiles across the full thickness and maximum cooling."""
    rows = read_table("profiles.csv")
    history = read_table("cooling_history.csv")
    fig, (ax_profile, ax_cooling) = plt.subplots(1, 2, figsize=(7.3, 3.0))
    times = np.unique(values(rows, "time_s"))
    positive = times[times > 0]
    displayed = positive[np.unique(np.linspace(0, len(positive)-1,
                                                 min(4, len(positive))).round().astype(int))]
    available_methods = methods(rows)
    for time_s in displayed:
        first = [r for r in rows if r["method"] == available_methods[0]
                 and float(r["time_s"]) == time_s]
        first.sort(key=lambda r: float(r["x_m"]))
        x = 1000*values(first, "x_m")
        reference = values(first, "reference_c")
        ax_profile.plot(x, reference, color=NAVY, lw=1.25, alpha=.75)
        for method in available_methods:
            group = [r for r in rows if r["method"] == method and float(r["time_s"]) == time_s]
            group.sort(key=lambda r: float(r["x_m"]))
            ax_profile.plot(1000*values(group, "x_m"), values(group, "temperature_c"),
                            color=COLOURS[method], lw=.9,
                            linestyle="--" if method == "backward_euler" else ":",
                            marker="^" if method == "backward_euler" else "o",
                            markersize=2.5, markerfacecolor="white",
                            markevery=max(1, len(group)//9))
        if len(reference):
            middle = int(np.argmax(reference))
            ax_profile.annotate(f"{time_s:g} s", (x[middle], reference[middle]),
                                xytext=(2, 4), textcoords="offset points", color=NAVY,
                                fontsize=7.2, ha="left")
    handles = [Line2D([], [], color=NAVY, label="Analytical", lw=1.3)]
    handles += [Line2D([], [], color=COLOURS[m], marker="^" if m == "backward_euler" else "o",
                       markersize=3, markerfacecolor="white", lw=.9, label=LABELS[m])
                for m in available_methods]
    ax_profile.legend(handles=handles, loc="upper center", fontsize=7.1, frameon=False,
                      bbox_to_anchor=(.5, -.30), ncol=3, handlelength=1.7, columnspacing=.9)
    ax_profile.set(xlabel="Position through full thickness (mm)", ylabel="Temperature (°C)")
    ax_profile.set_title("(a) Temperature profiles", loc="left", color=NAVY, fontsize=10)
    ymin, ymax = ax_profile.get_ylim()
    ax_profile.set_ylim(ymin, ymax + .06*(ymax-ymin))

    for index, method in enumerate(methods(history)):
        group = [r for r in history if r["method"] == method]
        group.sort(key=lambda r: float(r["time_s"]))
        if index == 0:
            ax_cooling.plot(values(group, "time_s"), values(group, "reference_c"),
                            color=NAVY, lw=1.5, label="Analytical")
        ax_cooling.plot(values(group, "time_s"), values(group, "max_temperature_c"),
                        color=COLOURS[method], lw=.9, linestyle="--",
                        marker="^" if method == "backward_euler" else "o",
                        markersize=3, markerfacecolor="white",
                        markevery=max(1, len(group)//12), label=LABELS[method])
    target = float(history[0]["target_c"])
    ax_cooling.axhline(target, color=GREY, linestyle=":", lw=.9)
    ax_cooling.text(.98, target+1.4, f"Target {target:g} °C", ha="right", fontsize=7.6,
                    color=GREY, transform=ax_cooling.get_yaxis_transform())
    ax_cooling.set(xlabel="Time (s)", ylabel="Maximum temperature (°C)")
    ax_cooling.set_title("(b) Uniform-initial-temperature cooling", loc="left", color=NAVY, fontsize=10)
    ax_cooling.legend(frameon=False, fontsize=7.5, loc="upper right")
    for ax in (ax_profile, ax_cooling):
        format_axes(ax)
    finish(fig, "temperature_profiles")


def convergence() -> None:
    """Separate spatial refinement from temporal error against a discrete mode."""
    fig, axes = plt.subplots(1, 2, figsize=(7.3, 2.9))
    for ax, filename, key in zip(axes, ("spatial_convergence.csv", "temporal_convergence.csv"),
                                 ("intervals", "dt_s")):
        rows = read_table(filename)
        for method in methods(rows):
            group = [r for r in rows if r["method"] == method]
            group.sort(key=lambda r: float(r[key]))
            # The declared spatial-convergence case uses full thickness 10 mm.
            x = 10/values(group, key) if key == "intervals" else 1000*values(group, key)
            y = values(group, "max_abs_error_c")
            ax.loglog(x, y, marker="o" if method == "ftcs" else "^", markersize=4,
                      lw=1.5, color=COLOURS[method], label=LABELS[method])
        ax.set_ylabel("Maximum absolute error (°C)")
        ax.xaxis.set_major_locator(FixedLocator(np.sort(np.unique(x))))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.legend(frameon=False, fontsize=8)
        format_axes(ax)
    axes[0].set_xlabel("Grid spacing, Δx (mm)")
    axes[0].set_title("(a) Spatial refinement", loc="left", fontsize=10, color=NAVY)
    axes[1].set_xlabel("Time step, Δt (ms)")
    axes[1].set_title("(b) Time refinement; discrete sine reference", loc="left", fontsize=10, color=NAVY)
    finish(fig, "convergence")


def performance() -> None:
    """Show measured runtime versus error and mark every eligible setting."""
    rows = read_table("candidate_comparison.csv")
    fig, ax = plt.subplots(figsize=(5.8, 3.5))
    for method in methods(rows):
        group = [r for r in rows if r["method"] == method]
        x, y = 1000*values(group, "median_runtime_s"), values(group, "max_abs_error_c")
        ax.scatter(x, y, c=COLOURS[method], marker="o" if method == "ftcs" else "^",
                   s=35, alpha=.8, label=LABELS[method], edgecolors="white", linewidths=.4)
    eligible = [r for r in rows if r["eligible"].lower() in ("true", "1", "yes")]
    if eligible:
        ax.scatter(1000*values(eligible, "median_runtime_s"), values(eligible, "max_abs_error_c"),
                   facecolors="none", edgecolors=NAVY, s=78, linewidths=.8,
                   label="Meets original criteria")
        summary_path = ROOT / "results" / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
        selected = summary.get("selected") or min(eligible, key=lambda row: float(row["median_runtime_s"]))
        ax.scatter([1000*float(selected["median_runtime_s"])], [float(selected["max_abs_error_c"])],
                   color=NAVY, marker="*", s=105, zorder=6, label="Final selection")
        initial = summary.get("initial_selection")
        if initial is not None:
            ax.scatter([1000*float(initial["median_runtime_s"])], [float(initial["max_abs_error_c"])],
                       color=ORANGE, marker="x", s=48, linewidths=1.3, zorder=6,
                       label="Initial choice (failed check)")
            ax.text(.025, .035, "Final choice includes a 0.8 °C baseline margin",
                    transform=ax.transAxes, fontsize=7.6, color=NAVY)
        ax.annotate(f"Final: {LABELS[selected['method']]}, N={selected['intervals']}",
                    (1000*float(selected["median_runtime_s"]), float(selected["max_abs_error_c"])),
                    xytext=(-10, -30), textcoords="offset points", fontsize=8, color=NAVY, ha="right",
                    arrowprops=dict(arrowstyle="-", lw=.6, color=NAVY))
    ax.axhline(1.0, color=GREY, lw=.9, linestyle=":", label="Original temperature limit: 1 °C")
    ax.set(xscale="log", yscale="log", xlabel="Median solver runtime (ms)",
           ylabel="Maximum temperature error (°C)")
    ax.set_title("Accuracy and computational cost", loc="left", fontsize=11, color=NAVY)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", framealpha=1,
              fontsize=7.7, loc="upper right")
    format_axes(ax)
    finish(fig, "performance")


def sensitivity() -> None:
    """Compare numerical and analytical crossing-time sensitivity to L and α."""
    rows = read_table("sensitivity.csv")
    parameters = list(dict.fromkeys(row["parameter"] for row in rows))
    fig, axes = plt.subplots(1, 2, figsize=(7.3, 2.8), sharey=True)
    for ax, parameter in zip(axes, parameters):
        group = [r for r in rows if r["parameter"] == parameter]
        group.sort(key=lambda r: float(r["multiplier"]))
        baseline = min(group, key=lambda row: abs(float(row["multiplier"])-1))
        baseline_reference = float(baseline["reference_time_s"])
        numerical_baseline = float(baseline["numerical_time_s"])
        x = values(group, "multiplier")
        ax.plot(x, values(group, "reference_time_s")/baseline_reference,
                color=NAVY, lw=1.5, marker="o", markersize=4, label="Analytical")
        ax.plot(x, values(group, "numerical_time_s")/numerical_baseline,
                color=TEAL, lw=1, linestyle="--", marker="x", markersize=5, label="Numerical")
        is_length = "length" in parameter.lower() or "thick" in parameter.lower()
        ax.set_xlabel("Thickness multiplier, L/L₀" if is_length else "Diffusivity multiplier, α/α₀")
        ax.set_title("(a) Thickness sensitivity" if is_length else "(b) Diffusivity sensitivity",
                     loc="left", fontsize=10, color=NAVY)
        ax.set_xticks(x)
        ax.legend(frameon=False, fontsize=8)
        format_axes(ax)
    axes[0].set_ylabel("Cooling time / baseline cooling time")
    finish(fig, "sensitivity")


def stability() -> None:
    """Display stable and intentionally unstable FTCS errors without clipping."""
    rows = read_table("stability.csv")
    fig, ax = plt.subplots(figsize=(5.8, 3.1))
    for requested_r in sorted(set(values(rows, "requested_r"))):
        group = [r for r in rows if float(r["requested_r"]) == requested_r]
        group.sort(key=lambda r: float(r["time_s"]))
        times, errors = values(group, "time_s"), values(group, "max_abs_error_c")
        positive = (errors > 0) & np.isfinite(errors)
        ax.semilogy(times[positive], errors[positive], color=TEAL if requested_r <= .5 else ORANGE,
                    lw=1.5, label=f"r = {requested_r:g}")
    ax.set(xlabel="Time (s)", ylabel="Maximum temperature error (°C)")
    ax.set_title("FTCS stability: alternating initial perturbation", loc="left", fontsize=11, color=NAVY)
    ax.legend(frameon=False, fontsize=9)
    format_axes(ax)
    finish(fig, "stability")


def optimisation() -> None:
    """Compare the same FTCS method with a loop or vectorized spatial update."""
    rows = read_table("optimisation.csv")
    rows.sort(key=lambda row: row["implementation"] != "loop")
    medians = 1000*values(rows, "median_runtime_s")
    minima, maxima = 1000*values(rows, "min_runtime_s"), 1000*values(rows, "max_runtime_s")
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    positions = np.arange(len(rows))
    bars = ax.bar(positions, medians, width=.52,
                  color=[ORANGE if r["implementation"] == "loop" else TEAL for r in rows],
                  yerr=np.vstack((medians-minima, maxima-medians)), capsize=4,
                  error_kw={"linewidth": .9, "ecolor": NAVY})
    for bar, runtime, high in zip(bars, medians, maxima):
        ax.annotate(f"{runtime:.2f} ms", (bar.get_x()+bar.get_width()/2, high),
                    xytext=(0, 5), textcoords="offset points", ha="center", fontsize=9, color=NAVY)
    ax.set_xticks(positions, ["Spatial loop" if r["implementation"] == "loop"
                             else "Vectorized update" for r in rows])
    ax.set(ylabel="Median solver runtime (ms)", ylim=(0, max(maxima)*1.22))
    ax.set_title("FTCS implementation improvement", loc="left", fontsize=11, color=NAVY)
    ax.text(.99, .96, "Whiskers: measured minimum–maximum", transform=ax.transAxes,
            ha="right", va="top", fontsize=7.7, color=GREY)
    format_axes(ax)
    finish(fig, "optimisation")


def main() -> None:
    """Render every project figure from the final saved experiment tables."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8.5,
        "axes.labelsize": 8.5, "axes.titlesize": 10,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "figure.facecolor": "white", "savefig.facecolor": "white",
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    for draw in (temperature_profiles, convergence, performance, sensitivity, stability, optimisation):
        draw()
    print(f"Saved six PNG/PDF figure pairs to {FIGURES}")


if __name__ == "__main__":
    main()

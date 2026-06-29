"""
Public plotting API for UQdash.

Dashboard modules should import plotting functions from uqdash.plots,
not directly from the submodules.
"""

from uqdash.plots.sensitivity import (
    plot_sensitivity_bar,
    plot_method_comparison_bar,
)

from uqdash.plots.distributions import (
    plot_parameter_scatter,
    plot_qoi_multi_comparison,
)

from uqdash.plots.projections import (
    plot_projection_grid,
    plot_3d_projection,
    plot_3d_projection_static,
)

from uqdash.plots.manifold import (
    plot_manifold_projection,
    plot_manifold_loadings,
)

from uqdash.plots.diagnostics import (
    plot_convergence_diagnostics,
)

from uqdash.plots.distributions import (
    plot_parameter_scatter,
    plot_qoi_multi_comparison,
    plot_uncertainty_histogram,
    plot_prediction_intervals,
)

from uqdash.plots.distributions import (
    plot_parameter_scatter,
    plot_qoi_multi_comparison,
    plot_uncertainty_histogram,
    plot_prediction_intervals,
    plot_exceedance_probability,
    plot_scenario_uncertainty_comparison,
)

from uqdash.plots.calibration import (
    plot_residual_sequence,
    plot_residual_histogram,
)

from uqdash.plots.calibration import (
    plot_residual_sequence,
    plot_residual_histogram,
    plot_calibration_fit,
)

from uqdash.plots.validation import (
    plot_observed_vs_predicted,
    plot_validation_fit,
    plot_validation_residuals,
)

from uqdash.plots.simulation import plot_simulation_trajectories
"""
Calibration plots.
"""

import math

import matplotlib.pyplot as plt

from uqdash.plots.common import resolve_colormap


def plot_calibration_fit(
    fit_df,
    selected_variables=None,
    colormap="viridis",
    custom_colors=None,
):
    """
    Plot observed vs fitted model values for each calibrated variable.
    """
    variables = list(fit_df["variable"].unique())

    if selected_variables:
        variables = [
            variable for variable in variables
            if variable in selected_variables
        ]

    n_variables = len(variables)
    ncols = min(2, n_variables)
    nrows = math.ceil(n_variables / ncols)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(6 * ncols, 4 * nrows),
        squeeze=False,
    )

    cmap = resolve_colormap(colormap, custom_colors)

    for i, variable in enumerate(variables):
        ax = axes.flat[i]
        group = fit_df[fit_df["variable"] == variable].sort_values("time")

        color = cmap(i / max(1, n_variables - 1))

        ax.scatter(
            group["time"],
            group["observed"],
            label="Observed",
            s=45,
            color=color,
            alpha=0.80,
        )

        ax.plot(
            group["time"],
            group["predicted"],
            label="Predicted",
            linewidth=2.5,
            color=color,
        )

        ax.set_title(variable)
        ax.set_xlabel("Time")
        ax.set_ylabel(variable)
        ax.legend()

    for ax in axes.flat[n_variables:]:
        ax.axis("off")

    fig.suptitle("Calibration Fit", fontsize=14)
    fig.tight_layout()

    return fig


def plot_residual_sequence(
    fit_df,
    selected_variables=None,
    colormap="viridis",
    custom_colors=None,
):
    """
    Plot residuals over time for each calibrated variable.
    """
    variables = list(fit_df["variable"].unique())

    if selected_variables:
        variables = [
            variable for variable in variables
            if variable in selected_variables
        ]

    n_variables = len(variables)
    ncols = min(2, n_variables)
    nrows = math.ceil(n_variables / ncols)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(6 * ncols, 4 * nrows),
        squeeze=False,
    )

    cmap = resolve_colormap(colormap, custom_colors)

    for i, variable in enumerate(variables):
        ax = axes.flat[i]
        group = fit_df[fit_df["variable"] == variable].sort_values("time")

        color = cmap(i / max(1, n_variables - 1))

        ax.scatter(
            group["time"],
            group["residual"],
            s=45,
            color=color,
            alpha=0.80,
        )

        ax.axhline(0, linestyle="--", linewidth=2)

        ax.set_title(f"{variable} residuals")
        ax.set_xlabel("Time")
        ax.set_ylabel("Residual")

    for ax in axes.flat[n_variables:]:
        ax.axis("off")

    fig.suptitle("Calibration Residuals", fontsize=14)
    fig.tight_layout()

    return fig


def plot_residual_histogram(
    fit_df,
    bins=30,
    bar_color="royalblue",
    bar_alpha=0.75,
):
    """
    Plot pooled residual distribution.
    """
    fig, ax = plt.subplots(figsize=(7, 4))

    ax.hist(
        fit_df["residual"],
        bins=bins,
        color=bar_color,
        alpha=bar_alpha,
        edgecolor="black",
    )

    ax.axvline(0, linestyle="--", linewidth=2)

    ax.set_xlabel("Residual")
    ax.set_ylabel("Frequency")
    ax.set_title("Pooled Calibration Residuals")

    fig.tight_layout()
    return fig
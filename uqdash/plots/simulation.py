"""
Simulation plots.
"""

import math

import matplotlib.pyplot as plt

from uqdash.plots.common import resolve_colormap


def plot_simulation_trajectories(
    simulation_df,
    selected_states=None,
    colormap="viridis",
    custom_colors=None,
    plot_style=None,
):
    """
    Plot each simulated state variable in its own panel.
    """
    state_columns = [
        column for column in simulation_df.columns
        if column != "time"
    ]

    if selected_states:
        state_columns = [
            state for state in state_columns
            if state in selected_states
        ]

    n_states = len(state_columns)

    ncols = min(2, n_states)
    nrows = math.ceil(n_states / ncols)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(6 * ncols, 4 * nrows),
        squeeze=False,
    )

    style_source = plot_style or custom_colors or {}

    cmap = resolve_colormap(
        cmap=colormap,
        custom_colors=style_source,
    )

    for i, state in enumerate(state_columns):
        ax = axes.flat[i]
        color = cmap(i / max(1, n_states - 1))

        ax.plot(
            simulation_df["time"],
            simulation_df[state],
            linewidth=2.5,
            color=color,
        )

        ax.set_title(state)
        ax.set_xlabel("Time")
        ax.set_ylabel(state)

    for ax in axes.flat[n_states:]:
        ax.axis("off")

    fig.suptitle("Model Simulation", fontsize=14)
    fig.tight_layout()

    return fig
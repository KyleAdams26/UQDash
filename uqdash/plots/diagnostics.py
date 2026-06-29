"""
Diagnostic plots.
"""

import matplotlib.pyplot as plt

from uqdash.plots.common import resolve_colormap


def plot_convergence_diagnostics(
    convergence_df,
    selected_parameters=None,
    colormap="viridis",
    custom_colors=None,
):
    """
    Plot sensitivity-index convergence as sample size increases.
    """
    fig, ax = plt.subplots(figsize=(9, 5))

    if selected_parameters:
        plot_df = convergence_df[
            convergence_df["parameter"].isin(selected_parameters)
        ]
    else:
        plot_df = convergence_df

    parameters = list(plot_df["parameter"].unique())
    cmap = resolve_colormap(colormap, custom_colors)

    for i, (parameter, group) in enumerate(plot_df.groupby("parameter")):
        group = group.sort_values("n_samples")

        color = cmap(i / max(1, len(parameters) - 1))

        ax.plot(
            group["n_samples"],
            group["value"],
            marker="o",
            linewidth=2,
            color=color,
            label=parameter,
        )

    metric = convergence_df["metric"].iloc[0]
    method = convergence_df["method"].iloc[0]

    ax.set_xscale("log", base=2)
    ax.set_xlabel("Base sample size")
    ax.set_ylabel(metric)
    ax.set_title(f"{method} Convergence Diagnostic")
    ax.legend()

    fig.tight_layout()
    return fig
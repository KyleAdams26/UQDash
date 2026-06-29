"""
Distribution and QoI comparison plots.
"""

import matplotlib.pyplot as plt

from uqdash.plots.common import resolve_colormap


def plot_parameter_scatter(
    samples,
    parameter,
    cmap="viridis",
    custom_colors=None,
):
    """
    Plot one parameter against QoI.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    scatter = ax.scatter(
        samples[parameter],
        samples["QoI"],
        c=samples["QoI"],
        cmap=resolve_colormap(cmap, custom_colors),
        alpha=0.5,
        s=10,
    )

    ax.set_xlabel(parameter)
    ax.set_ylabel("QoI")
    ax.set_title(f"{parameter} vs QoI")

    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("QoI")

    fig.tight_layout()
    return fig


def plot_qoi_multi_comparison(runs):
    """
    Compare QoI distributions from multiple analysis runs.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    for run in runs:
        ax.hist(
            run.samples["QoI"],
            bins=30,
            alpha=0.4,
            label=run.label,
        )

    ax.set_xlabel("QoI")
    ax.set_ylabel("Frequency")
    ax.set_title("QoI Distribution Comparison")
    ax.legend()

    fig.tight_layout()
    return fig

def plot_uncertainty_histogram(
    samples,
    qoi_column="QoI",
    bins=40,
    bar_color="royalblue",
    bar_alpha=0.75,
):
    """
    Plot propagated uncertainty in a scalar QoI.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    qoi = samples[qoi_column]

    ax.hist(
        qoi,
        bins=bins,
        color=bar_color,
        alpha=bar_alpha,
        edgecolor="black",
    )

    ax.axvline(qoi.median(), linestyle="--", linewidth=2, label="Median")
    ax.axvline(qoi.quantile(0.025), linestyle=":", linewidth=2, label="95% interval")
    ax.axvline(qoi.quantile(0.975), linestyle=":", linewidth=2)

    ax.set_xlabel(qoi_column)
    ax.set_ylabel("Frequency")
    ax.set_title("Uncertainty Propagation: QoI Distribution")
    ax.legend()

    fig.tight_layout()
    return fig


def plot_prediction_intervals(intervals_df):
    """
    Plot prediction intervals for a scalar QoI.
    """
    fig, ax = plt.subplots(figsize=(7, 4))

    y_positions = range(len(intervals_df))

    for y, (_, row) in zip(y_positions, intervals_df.iterrows()):
        ax.plot(
            [row["lower"], row["upper"]],
            [y, y],
            marker="o",
            linewidth=3,
        )

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(intervals_df["interval"])
    ax.set_xlabel("QoI")
    ax.set_ylabel("Prediction interval")
    ax.set_title("QoI Prediction Intervals")

    fig.tight_layout()
    return fig

def plot_exceedance_probability(exceedance_df, bar_color="royalblue", bar_alpha=0.85):
    """
    Plot exceedance probability for a threshold event.
    """
    probability = exceedance_df["percent"].iloc[0]
    event = exceedance_df["event"].iloc[0]

    fig, ax = plt.subplots(figsize=(6, 4))

    ax.bar(
        ["Probability"],
        [probability],
        color=bar_color,
        alpha=bar_alpha,
        edgecolor="black",
    )

    ax.set_ylim(0, 100)
    ax.set_ylabel("Percent")
    ax.set_title(f"Exceedance Probability\n{event}")

    ax.text(
        0,
        probability,
        f"{probability:.2f}%",
        ha="center",
        va="bottom",
        fontsize=12,
    )

    fig.tight_layout()
    return fig


def plot_scenario_uncertainty_comparison(summary_df):
    """
    Compare propagated QoI uncertainty across scenarios.

    Shows median, 50% interval, and 95% interval.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    y_positions = range(len(summary_df))

    for y, (_, row) in zip(y_positions, summary_df.iterrows()):
        # 95% interval
        ax.plot(
            [row["q025"], row["q975"]],
            [y, y],
            linewidth=3,
            alpha=0.4,
            label="95% interval" if y == 0 else None,
        )

        # 50% interval
        ax.plot(
            [row["q25"], row["q75"]],
            [y, y],
            linewidth=7,
            alpha=0.7,
            label="50% interval" if y == 0 else None,
        )

        # Median
        ax.scatter(
            row["median"],
            y,
            s=70,
            zorder=3,
            label="Median" if y == 0 else None,
        )

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(summary_df["scenario"])
    ax.set_xlabel("QoI")
    ax.set_title("Scenario Uncertainty Comparison")
    ax.legend()

    fig.tight_layout()
    return fig
"""
Validation plots.
"""

import matplotlib.pyplot as plt


def plot_observed_vs_predicted(
    validation_df,
    point_color="tab:blue",
    alpha=0.75,
):
    """
    Plot observed values against predicted values.
    """
    fig, ax = plt.subplots(figsize=(6, 6))

    ax.scatter(
        validation_df["observed"],
        validation_df["predicted"],
        s=45,
        alpha=alpha,
        color=point_color,
    )

    min_value = min(
        validation_df["observed"].min(),
        validation_df["predicted"].min(),
    )

    max_value = max(
        validation_df["observed"].max(),
        validation_df["predicted"].max(),
    )

    ax.plot(
        [min_value, max_value],
        [min_value, max_value],
        linestyle="--",
        linewidth=2,
        label="Perfect prediction",
    )

    ax.set_xlabel("Observed")
    ax.set_ylabel("Predicted")
    ax.set_title("Observed vs Predicted")
    ax.legend()

    fig.tight_layout()
    return fig


def plot_validation_fit(
    validation_df,
    data_color="tab:blue",
    fit_color="tab:orange",
    alpha=0.85,
):
    """
    Plot observed data and model predictions against time or observation index.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    if "time" in validation_df.columns:
        x = validation_df["time"]
        xlabel = "Time"
    else:
        x = validation_df.index
        xlabel = "Observation index"

    ax.scatter(
        x,
        validation_df["observed"],
        label="Observed data",
        s=45,
        color=data_color,
        alpha=alpha,
    )

    ax.plot(
        x,
        validation_df["predicted"],
        label="Model prediction",
        linewidth=2,
        color=fit_color,
    )

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Output")
    ax.set_title("Validation Fit")
    ax.legend()

    fig.tight_layout()
    return fig


def plot_validation_residuals(
    validation_df,
    point_color="tab:blue",
    alpha=0.75,
):
    """
    Plot validation residuals.
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    if "time" in validation_df.columns:
        x = validation_df["time"]
        xlabel = "Time"
    else:
        x = validation_df.index
        xlabel = "Observation index"

    ax.scatter(
        x,
        validation_df["residual"],
        s=45,
        alpha=alpha,
        color=point_color,
    )

    ax.axhline(0, linestyle="--", linewidth=2)

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Residual")
    ax.set_title("Validation Residuals")

    fig.tight_layout()
    return fig
"""
Sensitivity-analysis plots.
"""

import matplotlib.pyplot as plt


def plot_sensitivity_bar(
    results,
    method: str,
    bar_color="royalblue",
    bar_alpha=0.85,
    orientation="Vertical",
):
    """
    Plot the main sensitivity metric for the selected method.
    """
    if method in ["Sobol", "eFAST"]:
        metric = "ST"
        ylabel = "Total-order index"
    elif method == "Morris":
        metric = "mu_star"
        ylabel = "Morris mu_star"
    else:
        raise ValueError(f"Unsupported method: {method}")

    fig, ax = plt.subplots(figsize=(9, 5))

    if orientation == "Horizontal":
        sorted_results = results.sort_values(metric, ascending=True)

        ax.barh(
            sorted_results["parameter"],
            sorted_results[metric],
            color=bar_color,
            alpha=bar_alpha,
            edgecolor="black",
        )

        ax.set_xlabel(ylabel)

    else:
        sorted_results = results.sort_values(metric, ascending=False)

        ax.bar(
            sorted_results["parameter"],
            sorted_results[metric],
            color=bar_color,
            alpha=bar_alpha,
            edgecolor="black",
        )

        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=45)

    ax.set_title(f"{method} Sensitivity Ranking")
    fig.tight_layout()
    return fig


def plot_method_comparison_bar(runs, metric="ST"):
    """
    Compare sensitivity indices across compatible methods.
    """
    if not runs:
        raise ValueError("At least one run is required.")

    parameter_names = runs[0].results["parameter"].tolist()
    x_positions = range(len(parameter_names))

    fig, ax = plt.subplots(figsize=(10, 5))

    bar_width = 0.8 / len(runs)

    for i, run in enumerate(runs):
        if metric not in run.results.columns:
            raise ValueError(
                f"{run.method} results do not contain metric '{metric}'."
            )

        values = (
            run.results
            .set_index("parameter")
            .loc[parameter_names, metric]
            .values
        )

        shifted_positions = [x + i * bar_width for x in x_positions]

        ax.bar(
            shifted_positions,
            values,
            width=bar_width,
            label=run.method,
        )

    centered_positions = [
        x + bar_width * (len(runs) - 1) / 2
        for x in x_positions
    ]

    ax.set_xticks(centered_positions)
    ax.set_xticklabels(parameter_names, rotation=45, ha="right")
    ax.set_ylabel(metric)
    ax.set_title(f"Method Comparison Using {metric}")
    ax.legend()

    fig.tight_layout()
    return fig
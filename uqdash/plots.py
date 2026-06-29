"""
Plotting utilities for UQdash.
"""

import math

import matplotlib.pyplot as plt
import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap

def plot_sensitivity_bar(
    results,
    method: str,
    bar_color="tab:blue",
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
        ax.set_title(f"{method} Sensitivity Ranking")
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
        ax.set_title(f"{method} Sensitivity Ranking")
        ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    return fig


def plot_parameter_scatter(samples, parameter, cmap="viridis"):
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


def plot_projection_grid(samples, parameters, qoi_column="QoI", cmap="viridis"):
    """
    Pairwise projection plot.

    If more than two parameters are provided, all pairwise combinations are shown.
    If exactly two are provided, a single pairwise plot is shown.
    """
    if len(parameters) < 2:
        raise ValueError("Choose at least two parameters for projection plots.")

    pairs = [
        (parameters[i], parameters[j])
        for i in range(len(parameters))
        for j in range(i + 1, len(parameters))
    ]

    num_pairs = len(pairs)
    ncols = min(3, num_pairs)
    nrows = math.ceil(num_pairs / ncols)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(5 * ncols, 4 * nrows),
        squeeze=False,
        constrained_layout=True,
    )

    qoi = samples[qoi_column]
    scatter_handle = None

    for ax, (x_param, y_param) in zip(axes.flat, pairs):
        scatter_handle = ax.scatter(
            samples[x_param],
            samples[y_param],
            c=qoi,
            cmap=resolve_colormap(cmap, custom_colors),
            s=10,
            alpha=0.5,
        )

        ax.set_xlabel(x_param)
        ax.set_ylabel(y_param)
        ax.set_title(f"{x_param} vs {y_param}")

    for ax in axes.flat[num_pairs:]:
        ax.axis("off")

    if scatter_handle is not None:
        cbar = fig.colorbar(scatter_handle, ax=axes, shrink=0.8)
        cbar.set_label(qoi_column)

    fig.suptitle("Projection Plot Colored by QoI", fontsize=14)
    return fig


def _plotly_colorscale_from_cmap(cmap: str) -> str:
    """
    Convert common Matplotlib colormap names to Plotly colorscale names.
    """
    if cmap == "custom" and custom_colors:
        return custom_colors

    mapping = {
        "viridis": "Viridis",
        "plasma": "Plasma",
        "inferno": "Inferno",
        "magma": "Magma",
        "cividis": "Cividis",
        "turbo": "Turbo",
        "coolwarm": "RdBu",
    }

    return mapping.get(cmap, "Viridis")


def plot_3d_projection(samples, x_param, y_param, z_param, qoi_column="QoI", cmap="viridis"):
    """
    Interactive Plotly 3D projection.
    """
    fig = px.scatter_3d(
        samples,
        x=x_param,
        y=y_param,
        z=z_param,
        color=qoi_column,
        color_continuous_scale=_plotly_colorscale_from_cmap(cmap),
        opacity=0.6,
        title=f"3D Projection: {x_param}, {y_param}, {z_param}",
    )

    fig.update_traces(marker={"size": 3})

    fig.update_layout(
        scene={
            "xaxis_title": x_param,
            "yaxis_title": y_param,
            "zaxis_title": z_param,
        }
    )

    return fig


def plot_3d_projection_static(samples, x_param, y_param, z_param, qoi_column="QoI", cmap="viridis"):
    """
    Static Matplotlib 3D projection.
    """
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    scatter = ax.scatter(
        samples[x_param],
        samples[y_param],
        samples[z_param],
        c=samples[qoi_column],
        cmap=resolve_colormap(cmap, custom_colors),
        s=10,
        alpha=0.5,
    )

    ax.set_xlabel(x_param)
    ax.set_ylabel(y_param)
    ax.set_zlabel(z_param)
    ax.set_title(f"3D Projection: {x_param}, {y_param}, {z_param}")

    cbar = fig.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_label(qoi_column)

    fig.tight_layout()
    return fig


def plot_manifold_projection(embedding_df, color_values=None, color_label="QoI", cmap="viridis"):
    """
    Plot a 2D manifold embedding.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    if color_values is None:
        color_values = embedding_df["QoI"]

    scatter = ax.scatter(
        embedding_df["Dim1"],
        embedding_df["Dim2"],
        c=color_values,
        cmap=resolve_colormap(cmap, custom_colors),
        s=10,
        alpha=0.6,
    )

    ax.set_xlabel("Dim1")
    ax.set_ylabel("Dim2")
    ax.set_title(f"Manifold Projection Colored by {color_label}")

    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label(color_label)

    fig.tight_layout()
    return fig


def plot_manifold_loadings(loadings, component="Dim1", top_n=10, bar_color="tab:blue", bar_alpha=0.85):
    """
    Plot top loadings for linear dimensionality-reduction methods.
    """
    component_loadings = (
        loadings[component]
        .sort_values(key=lambda series: series.abs(), ascending=False)
        .head(top_n)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        component_loadings.index,
        component_loadings.values,
        color=bar_color,
        alpha=bar_alpha,
        edgecolor="black",
    )

    ax.set_ylabel("Loading")
    ax.set_title(f"Top {top_n} Loadings for {component}")
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    return fig


def plot_pca_projection(scores_df, cmap="viridis"):
    """
    Backward-compatible PCA projection plot.
    """
    return plot_manifold_projection(
        scores_df,
        color_values=scores_df["QoI"],
        color_label="QoI",
        cmap=resolve_colormap(cmap, custom_colors),
    )


def plot_pca_loadings(loadings, component="PC1", top_n=10, bar_color="tab:blue", bar_alpha=0.85):
    """
    Backward-compatible PCA loadings plot.
    """
    return plot_manifold_loadings(
        loadings=loadings,
        component=component,
        top_n=top_n,
        bar_color=bar_color,
        bar_alpha=bar_alpha,
    )


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

def plot_convergence_diagnostics(
    convergence_df,
    selected_parameters=None,
    colormap="viridis",
):
    """
    Plot sensitivity-index convergence as sample size increases.

    Uses the selected plot theme colormap so convergence diagnostics match
    the rest of the dashboard.
    """
    fig, ax = plt.subplots(figsize=(9, 5))

    if selected_parameters:
        plot_df = convergence_df[
            convergence_df["parameter"].isin(selected_parameters)
        ]
    else:
        plot_df = convergence_df

    parameters = list(plot_df["parameter"].unique())
    cmap = plt.get_cmap(colormap)

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

def resolve_colormap(cmap="viridis", custom_colors=None):
    """
    Return a Matplotlib colormap.

    If cmap == 'custom', build a colormap from user-selected colors.
    Otherwise, return the named Matplotlib colormap.
    """
    if cmap == "custom" and custom_colors:
        return LinearSegmentedColormap.from_list(
            "uqdash_custom_colormap",
            custom_colors,
        )

    return plt.get_cmap(cmap)
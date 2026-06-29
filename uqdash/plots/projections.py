"""
Pairwise and 3D projection plots.

These plots visualize parameter samples colored by the scalar QoI.

The optional qoi_min and qoi_max arguments control the color scale.
If they are None, Matplotlib/Plotly use the min and max QoI values
from the generated samples.
"""

import math

import matplotlib.pyplot as plt
import plotly.express as px

from uqdash.plots.common import (
    resolve_colormap,
    plotly_colorscale_from_cmap,
)


def plot_projection_grid(
    samples,
    parameters,
    qoi_column="QoI",
    cmap="viridis",
    custom_colors=None,
    qoi_min=None,
    qoi_max=None,
):
    """
    Create pairwise parameter projection plots colored by QoI.

    Parameters
    ----------
    samples:
        DataFrame containing sampled parameter values and a QoI column.

    parameters:
        List of parameter names to include in pairwise projections.

    qoi_column:
        Name of the QoI column used for coloring points.

    cmap:
        Matplotlib colormap name or "custom".

    custom_colors:
        Plot-style dictionary or list of custom colors.

    qoi_min, qoi_max:
        Optional color scale limits. If None, the plot uses the actual
        min/max of the QoI values.
    """
    if len(parameters) < 2:
        raise ValueError("Choose at least two parameters for projection plots.")

    # Build all unique parameter pairs.
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

    # Resolve preset or custom colormap.
    resolved_cmap = resolve_colormap(
        cmap=cmap,
        custom_colors=custom_colors,
    )

    for ax, (x_param, y_param) in zip(axes.flat, pairs):
        scatter_handle = ax.scatter(
            samples[x_param],
            samples[y_param],
            c=qoi,
            cmap=resolved_cmap,
            s=10,
            alpha=0.5,
            vmin=qoi_min,
            vmax=qoi_max,
        )

        ax.set_xlabel(x_param)
        ax.set_ylabel(y_param)
        ax.set_title(f"{x_param} vs {y_param}")

    # Hide unused subplot axes.
    for ax in axes.flat[num_pairs:]:
        ax.axis("off")

    if scatter_handle is not None:
        cbar = fig.colorbar(scatter_handle, ax=axes, shrink=0.8)
        cbar.set_label(qoi_column)

    fig.suptitle("Projection Plot Colored by QoI", fontsize=14)

    return fig


def plot_3d_projection(
    samples,
    x_param,
    y_param,
    z_param,
    qoi_column="QoI",
    cmap="viridis",
    custom_colors=None,
    qoi_min=None,
    qoi_max=None,
):
    """
    Create an interactive Plotly 3D projection colored by QoI.

    qoi_min and qoi_max control the Plotly color range.
    """
    # Plotly expects range_color=None or [min, max].
    color_range = None

    if qoi_min is not None and qoi_max is not None:
        color_range = [qoi_min, qoi_max]

    fig = px.scatter_3d(
        samples,
        x=x_param,
        y=y_param,
        z=z_param,
        color=qoi_column,
        color_continuous_scale=plotly_colorscale_from_cmap(
            cmap,
            custom_colors,
        ),
        range_color=color_range,
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


def plot_3d_projection_static(
    samples,
    x_param,
    y_param,
    z_param,
    qoi_column="QoI",
    cmap="viridis",
    custom_colors=None,
    qoi_min=None,
    qoi_max=None,
):
    """
    Create a static Matplotlib 3D projection colored by QoI.

    qoi_min and qoi_max control the Matplotlib color scale.
    """
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    scatter = ax.scatter(
        samples[x_param],
        samples[y_param],
        samples[z_param],
        c=samples[qoi_column],
        cmap=resolve_colormap(
            cmap=cmap,
            custom_colors=custom_colors,
        ),
        s=10,
        alpha=0.5,
        vmin=qoi_min,
        vmax=qoi_max,
    )

    ax.set_xlabel(x_param)
    ax.set_ylabel(y_param)
    ax.set_zlabel(z_param)
    ax.set_title(f"3D Projection: {x_param}, {y_param}, {z_param}")

    cbar = fig.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_label(qoi_column)

    fig.tight_layout()

    return fig
"""
Dimensionality-reduction and manifold plots.
"""

import matplotlib.pyplot as plt

from uqdash.plots.common import resolve_colormap


def plot_manifold_projection(
    embedding_df,
    color_values=None,
    color_label="QoI",
    cmap="viridis",
    custom_colors=None,
):
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


def plot_manifold_loadings(
    loadings,
    component="Dim1",
    top_n=10,
    bar_color="royalblue",
    bar_alpha=0.85,
):
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
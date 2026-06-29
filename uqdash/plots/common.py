"""
Common plotting utilities.
"""

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def get_custom_colors(plot_style_or_colors=None):
    """
    Extract custom colorwheel colors from either a plot-style dictionary
    or a direct list of colors.
    """
    if plot_style_or_colors is None:
        return []

    # Already a list/tuple of colors.
    if isinstance(plot_style_or_colors, (list, tuple)):
        return list(plot_style_or_colors)

    # Dashboard plot-style dictionary.
    if isinstance(plot_style_or_colors, dict):
        return (
            plot_style_or_colors.get("custom_colormap_colors")
            or plot_style_or_colors.get("custom_colors")
            or plot_style_or_colors.get("colorwheel_colors")
            or []
        )

    return []


def resolve_colormap(cmap="viridis", custom_colors=None):
    """
    Resolve a Matplotlib colormap.

    Supports:
    - standard Matplotlib colormap names
    - custom UQDash colorwheel themes
    """
    custom_colors = get_custom_colors(custom_colors)

    if cmap is None:
        return plt.get_cmap("viridis")

    cmap_name = str(cmap).lower()

    if cmap_name == "custom":
        if len(custom_colors) >= 2:
            return LinearSegmentedColormap.from_list(
                "uqdash_custom_colormap",
                custom_colors,
            )

        return plt.get_cmap("viridis")

    return plt.get_cmap(cmap)


def plotly_colorscale_from_cmap(cmap="viridis", custom_colors=None, n_colors=10):
    """
    Convert a Matplotlib colormap into a Plotly colorscale.
    """
    resolved_cmap = resolve_colormap(cmap, custom_colors)

    colorscale = []

    for i in range(n_colors):
        value = i / max(1, n_colors - 1)
        rgba = resolved_cmap(value)

        rgb_string = (
            f"rgb({int(255 * rgba[0])}, "
            f"{int(255 * rgba[1])}, "
            f"{int(255 * rgba[2])})"
        )

        colorscale.append([value, rgb_string])

    return colorscale


def get_two_plot_colors(plot_style: dict):
    """
    Resolve two colors for observed-vs-model plots.

    Used by calibration and validation plots.
    """
    custom_colors = get_custom_colors(plot_style)

    if len(custom_colors) >= 2:
        return custom_colors[0], custom_colors[1]

    if len(custom_colors) == 1:
        return custom_colors[0], plot_style.get("line_color", "tab:orange")

    observed_color = plot_style.get("bar_color", "tab:blue")
    model_color = plot_style.get("line_color", "tab:orange")

    return observed_color, model_color
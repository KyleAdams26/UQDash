"""
Sidebar controls for UQdash.

This file collects global dashboard settings:
    - model file path
    - sampling settings
    - plot theme / style settings

The main dashboard calls display_sidebar(), which returns one settings
dictionary used throughout the app.
"""

import streamlit as st


# -------------------------
# Theme definitions
# -------------------------
PLOT_THEMES = {
    "Default": {
        "bar_color": "royalblue",
        "line_color": "darkorange",
        "bar_alpha": 0.85,
        "bar_orientation": "Vertical",
        "colormap": "viridis",
    },
    "Publication": {
        "bar_color": "black",
        "line_color": "dimgray",
        "bar_alpha": 0.85,
        "bar_orientation": "Horizontal",
        "colormap": "cividis",
    },
    "Colorblind Safe": {
        "bar_color": "steelblue",
        "line_color": "darkorange",
        "bar_alpha": 0.85,
        "bar_orientation": "Horizontal",
        "colormap": "cividis",
    },
    "Vibrant": {
        "bar_color": "darkorange",
        "line_color": "royalblue",
        "bar_alpha": 0.85,
        "bar_orientation": "Vertical",
        "colormap": "turbo",
    },
    "Pastel": {
        "bar_color": "mediumpurple",
        "line_color": "mediumseagreen",
        "bar_alpha": 0.70,
        "bar_orientation": "Vertical",
        "colormap": "plasma",
    },
    "Monochrome": {
        "bar_color": "gray",
        "line_color": "black",
        "bar_alpha": 0.85,
        "bar_orientation": "Horizontal",
        "colormap": "gray",
    },
}


COLORMAPS = {
    "Viridis": "viridis",
    "Plasma": "plasma",
    "Inferno": "inferno",
    "Magma": "magma",
    "Cividis": "cividis",
    "Turbo": "turbo",
    "Coolwarm": "coolwarm",
    "Rainbow": "rainbow",
    "Grayscale": "gray",
    "Terrain": "terrain",
    "Ocean": "ocean",
}


# -------------------------
# Sidebar sections
# -------------------------
def display_model_settings() -> dict:
    """
    Display model-file controls.

    Returns:
        Dictionary containing the selected model path.
    """
    st.sidebar.header("Model File")

    model_path = st.sidebar.text_input(
        "Path to model file",
        value="examples/logistic_model.py",
    )

    return {
        "model_path": model_path,
    }


def display_sampling_settings() -> dict:
    """
    Display sampling controls.

    Returns:
        Dictionary containing sample size and random seed settings.
    """
    st.sidebar.header("Sampling")

    sample_power = st.sidebar.number_input(
        "Base sample size as 2^k",
        min_value=4,
        max_value=20,
        value=9,
        step=1,
    )

    n_samples = 2 ** sample_power

    seed = st.sidebar.number_input(
        "Random seed",
        min_value=0,
        value=1,
        step=1,
    )

    st.sidebar.write(f"Using base sample size: {n_samples}")

    return {
        "sample_power": sample_power,
        "n_samples": n_samples,
        "seed": seed,
    }


def display_plot_settings() -> dict:
    """
    Display plot-theme controls.

    Returns:
        Dictionary containing a plot_style dictionary.
    """
    st.sidebar.header("Plot Theme")

    theme_name = st.sidebar.selectbox(
        "Theme",
        list(PLOT_THEMES.keys()) + ["Custom"],
        index=0,
    )

    if theme_name == "Custom":
        plot_style = display_custom_plot_settings()
    else:
        plot_style = PLOT_THEMES[theme_name].copy()

    return {
        "plot_theme": theme_name,
        "plot_style": plot_style,
    }


def display_custom_plot_settings() -> dict:
    """
    Display custom plot-style controls.

    Returns:
        Dictionary matching the structure of a plot theme.
    """
    bar_color = st.sidebar.color_picker(
        "Primary plot color",
        value="#4169E1",  # royal blue
    )

    line_color = st.sidebar.color_picker(
        "Secondary / model-fit line color",
        value="#FF8C00",  # dark orange
    )

    bar_alpha = st.sidebar.slider(
        "Plot transparency",
        min_value=0.20,
        max_value=1.00,
        value=0.85,
        step=0.05,
    )

    bar_orientation = st.sidebar.selectbox(
        "Sensitivity bar orientation",
        ["Vertical", "Horizontal"],
        index=0,
    )

    colormap_mode = st.sidebar.radio(
        "Projection color map mode",
        ["Preset", "Custom"],
        horizontal=True,
    )

    if colormap_mode == "Preset":
        colormap_name = st.sidebar.selectbox(
            "Projection color map",
            list(COLORMAPS.keys()),
            index=0,
        )

        colormap = COLORMAPS[colormap_name]
        custom_colormap_colors = None

    else:
        num_colors = st.sidebar.slider(
            "Number of colors",
            min_value=2,
            max_value=8,
            value=3,
            step=1,
        )

        default_colors = [
            "#440154",
            "#3B528B",
            "#21918C",
            "#5EC962",
            "#FDE725",
            "#F97316",
            "#DC2626",
            "#7C3AED",
        ]

        custom_colormap_colors = []

        for i in range(num_colors):
            custom_colormap_colors.append(
                st.sidebar.color_picker(
                    f"Color {i + 1}",
                    value=default_colors[i],
                )
            )

        colormap = "custom"

    return {
        "bar_color": bar_color,
        "line_color": line_color,
        "bar_alpha": bar_alpha,
        "bar_orientation": bar_orientation,
        "colormap": colormap,
        "custom_colormap_colors": custom_colormap_colors,
        "custom_colors": custom_colormap_colors,
    }


def display_sidebar() -> dict:
    """
    Display all sidebar sections and return combined settings.

    This is the only function app.py needs to call.
    """
    model_settings = display_model_settings()
    sampling_settings = display_sampling_settings()
    plot_settings = display_plot_settings()

    # Merge all sidebar settings into one dictionary.
    return {
        **model_settings,
        **sampling_settings,
        **plot_settings,
    }
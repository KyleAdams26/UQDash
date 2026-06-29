"""
Dashboard UI for the Projection Explorer.
"""

from itertools import combinations

import streamlit as st

from uqdash.plots import (
    plot_projection_grid,
    plot_3d_projection,
    plot_3d_projection_static,
)


def display_projection_explorer(base_run) -> None:
    """
    Display projection explorer.

    Users choose parameters, then inspect either pairwise or 3D projections.
    """
    st.subheader("Projection Explorer")

    plot_style = st.session_state.get("plot_style", {})
    cmap = plot_style.get("colormap", "viridis")
    custom_colors = plot_style.get("custom_colormap_colors")

    available_parameters = list(base_run.samples.columns.drop("QoI"))

    projection_mode = st.radio(
        "Projection type",
        ["Pairwise", "3D"],
        horizontal=True,
        key="projection_explorer_mode",
    )

    projection_parameters = st.multiselect(
        "Choose parameters to explore",
        available_parameters,
        default=available_parameters[: min(5, len(available_parameters))],
        key="projection_explorer_parameters",
    )

    required_number = 2 if projection_mode == "Pairwise" else 3

    if len(projection_parameters) < required_number:
        st.info(
            f"Choose at least {required_number} parameters "
            f"for {projection_mode} projections."
        )
        return

    projection_combinations = list(
        combinations(projection_parameters, required_number)
    )

    combination_labels = [" vs ".join(combo) for combo in projection_combinations]

    selected_projection_label = st.selectbox(
        "Choose projection",
        combination_labels,
        key="projection_explorer_combination",
    )

    selected_index = combination_labels.index(selected_projection_label)
    selected_combo = projection_combinations[selected_index]

    st.write(
        f"Showing projection {selected_index + 1} "
        f"of {len(projection_combinations)}"
    )

    if projection_mode == "Pairwise":
        x_param, y_param = selected_combo

        st.pyplot(
            plot_projection_grid(
                base_run.samples,
                [x_param, y_param],
                cmap=cmap,
                custom_colors=custom_colors,
            )
        )

    else:
        x_param, y_param, z_param = selected_combo

        three_d_mode = st.radio(
            "3D rendering mode",
            ["Static (Matplotlib)", "Interactive (Plotly)"],
            horizontal=True,
            key="projection_explorer_3d_mode",
        )

        if three_d_mode == "Interactive (Plotly)":
            st.plotly_chart(
                plot_3d_projection(
                    base_run.samples,
                    x_param,
                    y_param,
                    z_param,
                    cmap=cmap,
                    custom_colors=custom_colors,
                ),
                use_container_width=True,
            )
        else:
            st.pyplot(
                plot_3d_projection_static(
                    base_run.samples,
                    x_param,
                    y_param,
                    z_param,
                    cmap=cmap,
                    custom_colors=custom_colors,
                )
            )
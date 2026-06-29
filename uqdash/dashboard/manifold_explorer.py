"""
Dashboard UI for the Parameter Manifold Explorer.
"""

import streamlit as st

from uqdash.exploration.manifold import run_manifold_projection
from uqdash.plots import (
    plot_manifold_projection,
    plot_manifold_loadings,
)


def display_manifold_explorer(base_run) -> None:
    """
    Display unified dimensionality-reduction explorer.

    Methods:
        PCA
        Active Subspaces placeholder
        t-SNE
        UMAP
    """
    st.subheader("Parameter Manifold Explorer")

    available_parameters = list(base_run.samples.columns.drop("QoI"))

    method = st.radio(
        "Dimensionality reduction method",
        ["PCA", "Active Subspaces", "t-SNE", "UMAP"],
        horizontal=True,
        key="manifold_method",
    )

    selected_parameters = st.multiselect(
        "Choose parameters",
        available_parameters,
        default=available_parameters[: min(5, len(available_parameters))],
        key="manifold_parameters",
    )

    color_by = st.radio(
        "Color by",
        ["QoI", "Parameter", "Sensitivity Index"],
        horizontal=True,
        key="manifold_color_by",
    )

    if len(selected_parameters) < 2:
        st.info("Choose at least two parameters.")
        return

    if method == "Active Subspaces":
        st.info(
            "Active Subspaces need gradients of QoI with respect to parameters. "
            "We will add this after UQdash supports finite-difference or "
            "user-supplied gradient evaluations."
        )
        return

    try:
        embedding_df, loadings, explained_variance = run_manifold_projection(
            method=method,
            samples=base_run.samples,
            parameter_names=selected_parameters,
            random_state=base_run.seed,
        )

    except Exception as e:
        st.error(f"Error running {method}: {e}")
        return

    color_values, color_label = get_color_values(
        base_run=base_run,
        selected_parameters=selected_parameters,
        color_by=color_by,
    )

    plot_style = st.session_state.get("plot_style", {})
    cmap = plot_style.get("colormap", "viridis")
    custom_colors = plot_style.get("custom_colormap_colors")

    st.pyplot(
        plot_manifold_projection(
            embedding_df,
            color_values=color_values,
            color_label=color_label,
            cmap=cmap,
            custom_colors=custom_colors,
        )
    )

    if explained_variance is not None:
        st.subheader("Explained Variance")
        st.dataframe(explained_variance)

    if loadings is not None:
        st.subheader("Loadings")

        component = st.selectbox(
            "Component for loadings plot",
            ["Dim1", "Dim2"],
            key="manifold_loadings_component",
        )

        top_n = st.number_input(
            "Number of top loadings",
            min_value=2,
            max_value=len(selected_parameters),
            value=min(10, len(selected_parameters)),
            step=1,
            key="manifold_top_n_loadings",
        )

        st.pyplot(
            plot_manifold_loadings(
                loadings=loadings,
                component=component,
                top_n=top_n,
                bar_color=plot_style.get("bar_color", "tab:blue"),
                bar_alpha=plot_style.get("bar_alpha", 0.85),
            )
        )
        st.dataframe(loadings)


def get_color_values(base_run, selected_parameters, color_by):
    """
    Determine color values for manifold plots.

    QoI: color by model output.
    Parameter: user chooses one sampled parameter.
    Sensitivity Index: color by each sample's selected parameter is not directly
    meaningful, so for now we show a note and fall back to QoI.
    """
    if color_by == "QoI":
        return base_run.samples["QoI"], "QoI"

    if color_by == "Parameter":
        parameter_to_color = st.selectbox(
            "Parameter to color by",
            selected_parameters,
            key="manifold_color_parameter",
        )

        return base_run.samples[parameter_to_color], parameter_to_color

    if color_by == "Sensitivity Index":
        st.info(
            "Sensitivity index is parameter-level, not sample-level. "
            "For now, UQdash colors the embedding by QoI. "
            "Later we can add parameter loading overlays."
        )

        return base_run.samples["QoI"], "QoI"

    return base_run.samples["QoI"], "QoI"
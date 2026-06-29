"""
Dashboard UI for convergence diagnostics.
"""

import streamlit as st

from uqdash.loader import load_model_from_path
from uqdash.diagnostics.convergence import run_convergence_diagnostic
from uqdash.plots import plot_convergence_diagnostics


def display_convergence_section(settings: dict) -> None:
    """
    Display convergence diagnostics for sensitivity indices.

    The user selects a method and a range of sample powers. UQdash reruns
    the analysis at each sample size and shows whether rankings stabilize.
    """
    st.subheader("Convergence Diagnostics")

    st.write(
        "Check whether sensitivity indices stabilize as the sample size increases. "
        "This helps diagnose whether the current sample size is large enough."
    )

    method = st.selectbox(
        "Method for convergence diagnostic",
        ["Sobol", "eFAST", "Morris"],
        key="convergence_method",
    )

    min_power = st.number_input(
        "Minimum sample power",
        min_value=4,
        max_value=20,
        value=6,
        step=1,
        key="convergence_min_power",
    )

    max_power = st.number_input(
        "Maximum sample power",
        min_value=4,
        max_value=20,
        value=10,
        step=1,
        key="convergence_max_power",
    )

    if max_power < min_power:
        st.warning("Maximum sample power must be at least the minimum sample power.")
        return

    sample_powers = list(range(min_power, max_power + 1))

    st.write(
        "Sample sizes: "
        + ", ".join([str(2 ** power) for power in sample_powers])
    )

    if st.button("Run Convergence Diagnostic", key="run_convergence_diagnostic"):
        try:
            model_module = load_model_from_path(settings["model_path"])

            with st.spinner("Running convergence diagnostic..."):
                convergence_df, convergence_runs = run_convergence_diagnostic(
                    method=method,
                    model_module=model_module,
                    model_path=settings["model_path"],
                    sample_powers=sample_powers,
                    seed=settings["seed"],
                )

            st.session_state["convergence_df"] = convergence_df
            st.session_state["convergence_runs"] = convergence_runs

            st.success("Finished convergence diagnostic!")

        except Exception as e:
            st.error(f"Error: {e}")

    if "convergence_df" in st.session_state:
        convergence_df = st.session_state["convergence_df"]

        available_parameters = sorted(convergence_df["parameter"].unique())

        selected_parameters = st.multiselect(
            "Parameters to display",
            available_parameters,
            default=available_parameters[: min(5, len(available_parameters))],
            key="convergence_selected_parameters",
        )

        plot_style = st.session_state.get("plot_style", {})

        st.pyplot(
            plot_convergence_diagnostics(
                convergence_df,
                selected_parameters=selected_parameters,
                colormap=plot_style.get("colormap",
                 "viridis"),
                 custom_colors=plot_style.get("custom_colormap_colors"),
            )
        )

        st.subheader("Convergence Table")
        st.dataframe(convergence_df)
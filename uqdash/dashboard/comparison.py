import json

import streamlit as st

from uqdash.loader import load_model_from_path
from uqdash.comparison import run_comparison
from uqdash.plots import (
    plot_qoi_multi_comparison,
    plot_sensitivity_bar,
)
from uqdash.dashboard.parameters import display_parameter_summary


def display_comparison_section(settings: dict, base_run) -> None:
    """
    Display QoI distribution comparison workflow.

    The user selects parameters to keep varying. Every other parameter is
    frozen at its nominal value.
    """
    st.subheader("QoI Distribution Comparison")

    st.write(
        "Select parameters to keep varying. All other parameters will be frozen "
        "at their nominal values. This helps test whether a smaller influential "
        "subset explains most of the QoI variation."
    )

    # Rank parameters by user-specified method's ranking.
    sensitivity_ranking = base_run.top_parameters()

    kept_parameters = st.multiselect(
        "Parameters to keep varying",
        sensitivity_ranking,
        default=sensitivity_ranking[: min(5, len(sensitivity_ranking))],
        key="parameter_analysis_kept_parameters",
    )

    comparison_label = st.text_input(
        "Scenario label",
        value="Only selected parameters varied",
        key="parameter_analysis_comparison_label",
    )

    include_full_model = st.checkbox(
        "Include full model with all parameters varied",
        value=True,
        key="parameter_analysis_include_full_model",
    )

    if st.button("Run Parameter Comparison", key="run_parameter_comparison_button"):
        run_parameter_comparison(
            settings=settings,
            kept_parameters=kept_parameters,
            comparison_label=comparison_label,
            include_full_model=include_full_model,
        )

    if "comparison_runs" in st.session_state:
        display_comparison_results(st.session_state["comparison_runs"])


def run_parameter_comparison(
    settings: dict,
    kept_parameters: list[str],
    comparison_label: str,
    include_full_model: bool,
) -> None:
    """
    Run QoI distribution comparison for selected varying parameters.
    """
    try:
        model_module = load_model_from_path(settings["model_path"])
        all_parameters = list(model_module.PARAMETERS.keys())

        # Freeze everything except the selected parameters.
        frozen_parameters = [
            param for param in all_parameters
            if param not in kept_parameters
        ]

        scenarios = []

        if include_full_model:
            scenarios.append(
                {
                    "label": "All parameters varied",
                    "frozen_parameters": [],
                }
            )

        scenarios.append(
            {
                "label": comparison_label,
                "frozen_parameters": frozen_parameters,
            }
        )

        with st.spinner("Running parameter comparison..."):
            comparison_runs = run_comparison(
                model_module=model_module,
                model_path=settings["model_path"],
                scenarios=scenarios,
                n_samples=settings["n_samples"],
                seed=settings["seed"],
            )

        st.session_state["comparison_runs"] = comparison_runs
        st.success("Finished parameter comparison!")

    except Exception as e:
        st.error(f"Error: {e}")


def display_comparison_results(runs) -> None:
    """
    Display comparison plots, tables, and export buttons.
    """
    st.pyplot(plot_qoi_multi_comparison(runs))

    selected_label = st.selectbox(
        "Inspect comparison scenario",
        [run.label for run in runs],
        key="comparison_scenario_selectbox",
    )

    comparison_run = next(run for run in runs if run.label == selected_label)

    st.write(f"Frozen parameters: {comparison_run.frozen_parameters}")
    st.write(f"Base sample size: {comparison_run.n_samples}")
    st.write(f"Estimated model evaluations: {comparison_run.estimated_runs:,}")
    st.write(f"Seed: {comparison_run.seed}")

    st.subheader("Scenario Sobol Indices")
    st.dataframe(comparison_run.results)

    st.subheader(f"Scenario {comparison_run.method} Sensitivity")    
    plot_style = st.session_state.get("plot_style", {})

    st.pyplot(
        plot_sensitivity_bar(
            comparison_run.results,
            comparison_run.method,
            bar_color=plot_style.get("bar_color", "tab:blue"),
            bar_alpha=plot_style.get("bar_alpha", 0.85),
            orientation=plot_style.get("bar_orientation", "Vertical"),
        )
    )

    st.subheader("Export Selected Comparison Scenario")

    safe_label = comparison_run.label.lower().replace(" ", "_").replace(":", "")

    st.download_button(
        label="Download Comparison Sobol Results CSV",
        data=comparison_run.results_csv(),
        file_name=f"{safe_label}_sobol_results.csv",
        mime="text/csv",
        key="comparison_download_results",
    )

    st.download_button(
        label="Download Comparison Samples CSV",
        data=comparison_run.samples_csv(),
        file_name=f"{safe_label}_simulation_samples.csv",
        mime="text/csv",
        key="comparison_download_samples",
    )

    st.download_button(
        label="Download Comparison Metadata JSON",
        data=json.dumps(comparison_run.metadata(), indent=4),
        file_name=f"{safe_label}_metadata.json",
        mime="application/json",
        key="comparison_download_metadata",
    )
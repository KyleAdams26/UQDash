"""
Dashboard UI for the Sensitivity Analysis tab.
"""

import json

import streamlit as st

from uqdash.loader import load_model_from_path
from uqdash.comparison import run_comparison
from uqdash.plots import plot_sensitivity_bar
from uqdash.dashboard.parameters import display_parameter_summary
from uqdash.dashboard.method_comparison import display_method_comparison_section
from uqdash.dashboard.convergence import display_convergence_section
from uqdash.reports.sensitivity_report import generate_sensitivity_report


def display_sensitivity_tab(settings: dict) -> None:
    """
    Display the full sensitivity-analysis workflow.

    The report export controls are placed at the bottom of the tab so the
    workflow reads naturally: run analysis, compare methods, check convergence,
    then export.
    """
    # Store plot style globally so other dashboard components can reuse it.
    st.session_state["plot_style"] = settings["plot_style"]

    st.header("Sensitivity Analysis")

    analysis_method = st.selectbox(
        "Sensitivity analysis method",
        ["Sobol", "Morris", "eFAST"],
        key="sensitivity_method_selectbox",
    )

    if st.button(f"Run {analysis_method} Analysis", key="run_sensitivity_button"):
        run_sensitivity_analysis(settings, analysis_method)

    # Main sensitivity results.
    if "sensitivity_run" in st.session_state:
        display_sensitivity_results(st.session_state["sensitivity_run"])

    st.divider()

    # Optional comparison across sensitivity methods.
    display_method_comparison_section(settings)

    st.divider()

    # Optional convergence diagnostic.
    display_convergence_section(settings)

    # Put report generation last, after the full sensitivity workflow.
    if "sensitivity_run" in st.session_state:
        st.divider()
        display_sensitivity_report_export(
            run=st.session_state["sensitivity_run"],
        )


def run_sensitivity_analysis(settings: dict, method: str) -> None:
    """
    Run a sensitivity analysis with all parameters varied.
    """
    try:
        model_module = load_model_from_path(settings["model_path"])

        # The main sensitivity run varies every parameter.
        scenarios = [
            {
                "label": "All parameters varied",
                "frozen_parameters": [],
            }
        ]

        with st.spinner(f"Running {method} analysis..."):
            sensitivity_runs = run_comparison(
                method=method,
                model_module=model_module,
                model_path=settings["model_path"],
                scenarios=scenarios,
                n_samples=settings["n_samples"],
                seed=settings["seed"],
            )

        st.session_state["sensitivity_run"] = sensitivity_runs[0]

        # Keep a Sobol run available for older parts of the dashboard
        # that may still use Sobol rankings.
        if method == "Sobol":
            st.session_state["sobol_run"] = sensitivity_runs[0]

            # Avoid using stale parameter-comparison runs from an older Sobol run.
            if "comparison_runs" in st.session_state:
                del st.session_state["comparison_runs"]

        st.success(f"Finished {method} analysis!")

    except Exception as e:
        st.error(f"Error: {e}")


def display_sensitivity_results(run) -> None:
    """
    Display sensitivity results, figures, and direct download buttons.
    """
    plot_style = st.session_state.get("plot_style", {})

    st.subheader(f"{run.method} Results")

    st.write(f"Base sample size: {run.n_samples}")
    st.write(f"Estimated model evaluations: {run.estimated_runs:,}")
    st.write(f"Seed: {run.seed}")

    display_parameter_summary(run.parameter_info)

    st.subheader("Sensitivity Indices")
    st.dataframe(run.results, use_container_width=True, hide_index=True)

    st.subheader("Sensitivity Ranking")

    # Build the ranking figure once for display.
    # The report generator recreates the same figure later so the export
    # controls can live at the bottom of the tab.
    sensitivity_fig = make_sensitivity_figure(run)
    st.pyplot(sensitivity_fig)

    st.subheader("Download Sensitivity Run")

    safe_method = run.method.lower().replace(" ", "_")
    safe_label = run.label.lower().replace(" ", "_").replace(":", "")

    st.download_button(
        label="Download Sensitivity Results CSV",
        data=run.results_csv(),
        file_name=f"{safe_method}_{safe_label}_results.csv",
        mime="text/csv",
        key="sensitivity_download_results",
    )

    st.download_button(
        label="Download Simulation Samples CSV",
        data=run.samples_csv(),
        file_name=f"{safe_method}_{safe_label}_simulation_samples.csv",
        mime="text/csv",
        key="sensitivity_download_samples",
    )

    st.download_button(
        label="Download Metadata JSON",
        data=json.dumps(run.metadata(), indent=4),
        file_name=f"{safe_method}_{safe_label}_metadata.json",
        mime="application/json",
        key="sensitivity_download_metadata",
    )


def make_sensitivity_figure(run):
    """
    Create the sensitivity-ranking figure using the current dashboard style.
    """
    plot_style = st.session_state.get("plot_style", {})

    return plot_sensitivity_bar(
        run.results,
        run.method,
        bar_color=plot_style.get("bar_color", "tab:blue"),
        bar_alpha=plot_style.get("bar_alpha", 0.85),
        orientation=plot_style.get("bar_orientation", "Vertical"),
    )


def display_sensitivity_report_export(run) -> None:
    """
    Display controls for generating a full sensitivity-analysis report.
    """
    st.subheader("Generate Sensitivity Report")

    output_root = st.text_input(
        "Report output folder",
        value="reports",
        key="sensitivity_report_output_folder",
    )

    figure_formats = st.multiselect(
        "Figure formats",
        ["png", "pdf", "jpg", "svg", "eps"],
        default=["png", "pdf"],
        key="sensitivity_report_figure_formats",
    )

    if not figure_formats:
        st.warning("Choose at least one figure format.")
        return

    # Recreate the ranking figure here so the report saves the same style
    # even though the report controls are placed below other dashboard sections.
    sensitivity_fig = make_sensitivity_figure(run)

    if st.button(
        "Generate Sensitivity Report",
        key="generate_sensitivity_report",
        type="primary",
    ):
        report_dir = generate_sensitivity_report(
            output_root=output_root,
            run=run,
            sensitivity_fig=sensitivity_fig,
            figure_formats=figure_formats,
        )

        st.success(f"Saved report to: {report_dir}")
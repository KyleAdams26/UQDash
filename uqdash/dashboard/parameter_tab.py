"""
Dashboard UI for the Parameter Analysis tab.

This tab generates independent parameter samples, evaluates the model QoI,
and lets the user explore parameter-QoI relationships through scatter plots,
pairwise projections, and 3D projections.
"""

import pandas as pd
import streamlit as st

from uqdash.loader import load_model_from_path
from uqdash.uncertainty.sampling import (
    generate_uncertainty_samples,
    evaluate_uncertainty_samples,
)
from uqdash.uncertainty.propagation import (
    summarize_qoi_uncertainty,
    compute_prediction_intervals,
)
from uqdash.plots import (
    plot_parameter_scatter,
    plot_projection_grid,
    plot_3d_projection,
    plot_3d_projection_static,
)
from uqdash.reports.parameter_analysis_report import (
    generate_parameter_analysis_report,
)
from uqdash.dashboard.parameter_ordering import order_parameters_by_sobol
from uqdash.uncertainty.sampling import (
    generate_uncertainty_samples,
    generate_selected_parameter_samples,
    evaluate_uncertainty_samples,
)
from uqdash.plots import plot_qoi_multi_comparison


def display_parameter_tab(settings: dict) -> None:
    """
    Display the parameter-analysis workflow.
    """
    st.header("Parameter Analysis")

    st.write(
        "Generate parameter samples, evaluate the model, and explore how "
        "parameter values relate to the quantity of interest."
    )

    display_parameter_analysis_controls(settings)

    if "parameter_analysis_samples" in st.session_state:
        display_parameter_analysis_results(
            st.session_state["parameter_analysis_samples"]
        )


def display_parameter_analysis_controls(settings: dict) -> None:
    """
    Display controls for running parameter analysis.
    """
    st.subheader("Run Parameter Analysis")

    sampler = st.selectbox(
        "Sampling method",
        ["Sobol QMC", "Latin Hypercube", "Random Monte Carlo"],
        key="parameter_analysis_sampler",
    )

    sample_power = st.number_input(
        "Sample size as 2^k",
        min_value=4,
        max_value=20,
        value=10,
        step=1,
        key="parameter_analysis_sample_power",
    )

    n_samples = 2 ** sample_power

    seed = st.number_input(
        "Random seed",
        min_value=0,
        value=settings.get("seed", 1),
        step=1,
        key="parameter_analysis_seed",
    )

    st.write(f"Using parameter-analysis sample size: {n_samples}")

    if st.button(
        "Run Parameter Analysis",
        key="run_parameter_analysis",
        type="primary",
    ):
        run_parameter_analysis(
            settings=settings,
            sampler=sampler,
            n_samples=n_samples,
            seed=seed,
        )


def run_parameter_analysis(
    settings: dict,
    sampler: str,
    n_samples: int,
    seed: int,
) -> None:
    """
    Generate parameter samples and evaluate the model QoI.
    """
    try:
        model_module = load_model_from_path(settings["model_path"])

        with st.spinner("Generating parameter samples..."):
            parameter_samples = generate_uncertainty_samples(
                model_module=model_module,
                n_samples=n_samples,
                seed=seed,
                sampler=sampler,
            )

        with st.spinner("Evaluating model on parameter samples..."):
            parameter_analysis_samples = evaluate_uncertainty_samples(
                model_module=model_module,
                parameter_samples=parameter_samples,
            )

        st.session_state["parameter_analysis_samples"] = parameter_analysis_samples
        st.session_state["parameter_analysis_metadata"] = {
            "model_path": settings["model_path"],
            "sampler": sampler,
            "n_samples": n_samples,
            "seed": seed,
        }

        st.success("Finished parameter analysis!")

    except Exception as e:
        st.error(f"Error: {e}")


def display_parameter_analysis_results(samples: pd.DataFrame) -> None:
    """
    Display parameter-analysis summaries, plots, and report export.
    """
    plot_style = st.session_state.get("plot_style", {})
    metadata = st.session_state.get("parameter_analysis_metadata", {})

    parameter_names = order_parameters_by_sobol([
        column for column in samples.columns
        if column != "QoI"
    ])

    st.subheader("Run Metadata")
    st.write(f"Sampling method: {metadata.get('sampler')}")
    st.write(f"Sample size: {metadata.get('n_samples')}")
    st.write(f"Seed: {metadata.get('seed')}")

    st.divider()

    summary_df = summarize_qoi_uncertainty(samples)
    intervals_df = compute_prediction_intervals(samples)

    st.subheader("QoI Summary Statistics")
    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Prediction Intervals")
    st.dataframe(
        intervals_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    display_scenario_qoi_comparison(
        samples=samples,
        parameter_names=parameter_names,
    )
    st.divider()

    qoi_min, qoi_max = display_qoi_color_scale_controls(samples)

    st.divider()

    scatter_fig = display_single_parameter_scatter(
        samples=samples,
        parameter_names=parameter_names,
        plot_style=plot_style,
        qoi_min=qoi_min,
        qoi_max=qoi_max,
    )

    st.divider()

    projection_fig, selected_projection_parameters = display_pairwise_projections(
        samples=samples,
        parameter_names=parameter_names,
        plot_style=plot_style,
        qoi_min=qoi_min,
        qoi_max=qoi_max,
    )

    st.divider()

    projection_3d_fig = display_3d_projection_section(
        samples=samples,
        parameter_names=parameter_names,
        plot_style=plot_style,
        qoi_min=qoi_min,
        qoi_max=qoi_max,
    )

    st.divider()

    display_parameter_report_export(
        metadata=metadata,
        summary_df=summary_df,
        intervals_df=intervals_df,
        samples=samples,
        scatter_fig=scatter_fig,
        projection_fig=projection_fig,
        projection_3d_fig=projection_3d_fig,
        selected_projection_parameters=selected_projection_parameters,
        qoi_min=qoi_min,
        qoi_max=qoi_max,
    )

def display_scenario_qoi_comparison(samples: pd.DataFrame, parameter_names) -> None:
    """
    Compare the QoI distribution from the full parameter set against a
    user-selected subset of varying parameters.

    The full run is the already-generated parameter-analysis sample.
    The selected-parameter run varies only the chosen parameters and fixes
    all other parameters at their nominal values.
    """
    st.subheader("Scenario QoI Comparison")

    st.write(
        "Compare the QoI distribution when all parameters vary against the "
        "QoI distribution when only selected parameters vary."
    )

    selected_parameters = st.multiselect(
        "Parameters to vary in selected-parameter scenario",
        parameter_names,
        default=parameter_names[: min(5, len(parameter_names))],
        key="parameter_analysis_scenario_parameters",
    )

    if not selected_parameters:
        st.warning("Choose at least one parameter to vary.")
        return

    metadata = st.session_state.get("parameter_analysis_metadata", {})

    sampler = metadata.get("sampler", "Sobol QMC")
    n_samples = int(metadata.get("n_samples", len(samples)))
    seed = int(metadata.get("seed", 1))

    if st.button(
        "Run Selected-Parameter Comparison",
        key="run_selected_parameter_comparison",
        type="primary",
    ):
        try:
            model_module = load_model_from_path(metadata["model_path"])

            with st.spinner("Generating selected-parameter samples..."):
                selected_parameter_samples = generate_selected_parameter_samples(
                    model_module=model_module,
                    varying_parameters=selected_parameters,
                    n_samples=n_samples,
                    seed=seed,
                    sampler=sampler,
                )

            with st.spinner("Evaluating selected-parameter scenario..."):
                selected_samples = evaluate_uncertainty_samples(
                    model_module=model_module,
                    parameter_samples=selected_parameter_samples,
                )

            st.session_state["parameter_analysis_scenario_samples"] = selected_samples
            st.session_state["parameter_analysis_scenario_metadata"] = {
                "varying_parameters": list(selected_parameters),
                "sampler": sampler,
                "n_samples": n_samples,
                "seed": seed,
            }

            st.success("Finished selected-parameter comparison!")

        except Exception as e:
            st.error(f"Error: {e}")

    if "parameter_analysis_scenario_samples" not in st.session_state:
        return

    selected_samples = st.session_state["parameter_analysis_scenario_samples"]

    comparison_runs = [
        SimpleComparisonRun(
            label="All parameters varied",
            method="Full",
            samples=samples,
        ),
        SimpleComparisonRun(
            label="Selected parameters varied",
            method="Selected",
            samples=selected_samples,
        ),
    ]

    comparison_fig = plot_qoi_multi_comparison(comparison_runs)

    st.pyplot(comparison_fig)

    summary_df = pd.DataFrame([
        summarize_scenario_qoi("All parameters varied", samples),
        summarize_scenario_qoi("Selected parameters varied", selected_samples),
    ])

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
    )

def display_qoi_color_scale_controls(samples: pd.DataFrame):
    """
    Let the user set the QoI color scale for projection plots.

    Defaults are the generated QoI minimum and maximum.
    """
    st.subheader("QoI Color Scale")

    qoi_min_default = float(samples["QoI"].min())
    qoi_max_default = float(samples["QoI"].max())

    col1, col2 = st.columns(2)

    with col1:
        qoi_min = st.number_input(
            "QoI color minimum",
            value=qoi_min_default,
            key="parameter_analysis_qoi_color_min",
        )

    with col2:
        qoi_max = st.number_input(
            "QoI color maximum",
            value=qoi_max_default,
            key="parameter_analysis_qoi_color_max",
        )

    if qoi_max <= qoi_min:
        st.warning("QoI color maximum must be greater than QoI color minimum.")
        st.stop()

    return qoi_min, qoi_max


def display_single_parameter_scatter(
    samples: pd.DataFrame,
    parameter_names,
    plot_style: dict,
    qoi_min: float,
    qoi_max: float,
):
    """
    Display a single parameter-vs-QoI scatter plot.
    """
    st.subheader("Single Parameter Scatter")

    selected_parameter = st.selectbox(
        "Parameter",
        parameter_names,
        key="parameter_analysis_single_parameter",
    )

    try:
        scatter_fig = plot_parameter_scatter(
            samples,
            selected_parameter,
            cmap=plot_style.get("colormap", "viridis"),
            custom_colors=plot_style,
            qoi_min=qoi_min,
            qoi_max=qoi_max,
        )

    except TypeError:
        # Backward-compatible fallback if plot_parameter_scatter has not yet
        # been updated to accept qoi_min/qoi_max.
        scatter_fig = plot_parameter_scatter(
            samples,
            selected_parameter,
            cmap=plot_style.get("colormap", "viridis"),
            custom_colors=plot_style,
        )

    st.pyplot(scatter_fig)

    return scatter_fig


def display_pairwise_projections(
    samples: pd.DataFrame,
    parameter_names,
    plot_style: dict,
    qoi_min: float,
    qoi_max: float,
):
    """
    Display pairwise projection plots colored by QoI.
    """
    st.subheader("Pairwise Projection Plots")

    selected_projection_parameters = st.multiselect(
        "Parameters to include in projection grid",
        parameter_names,
        default=parameter_names[: min(4, len(parameter_names))],
        key="parameter_analysis_projection_parameters",
    )

    if len(selected_projection_parameters) < 2:
        st.warning("Choose at least two parameters for pairwise projections.")
        return None, selected_projection_parameters

    projection_fig = plot_projection_grid(
        samples,
        selected_projection_parameters,
        cmap=plot_style.get("colormap", "viridis"),
        custom_colors=plot_style,
        qoi_min=qoi_min,
        qoi_max=qoi_max,
    )

    st.pyplot(projection_fig)

    return projection_fig, selected_projection_parameters


def display_3d_projection_section(
    samples: pd.DataFrame,
    parameter_names,
    plot_style: dict,
    qoi_min: float,
    qoi_max: float,
):
    """
    Display static or interactive 3D projection plot.
    """
    st.subheader("3D Projection Plot")

    if len(parameter_names) < 3:
        st.info("At least three parameters are required for a 3D projection.")
        return None

    projection_mode = st.radio(
        "3D plot type",
        ["Static", "Interactive"],
        horizontal=True,
        key="parameter_analysis_3d_projection_mode",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        x_param = st.selectbox(
            "x parameter",
            parameter_names,
            index=0,
            key="parameter_analysis_3d_x",
        )

    with col2:
        y_param = st.selectbox(
            "y parameter",
            parameter_names,
            index=1 if len(parameter_names) > 1 else 0,
            key="parameter_analysis_3d_y",
        )

    with col3:
        z_param = st.selectbox(
            "z parameter",
            parameter_names,
            index=2 if len(parameter_names) > 2 else 0,
            key="parameter_analysis_3d_z",
        )

    if len({x_param, y_param, z_param}) < 3:
        st.warning("Choose three distinct parameters for the 3D projection.")
        return None

    if projection_mode == "Interactive":
        projection_3d_fig = plot_3d_projection(
            samples,
            x_param=x_param,
            y_param=y_param,
            z_param=z_param,
            cmap=plot_style.get("colormap", "viridis"),
            custom_colors=plot_style,
            qoi_min=qoi_min,
            qoi_max=qoi_max,
        )

        st.plotly_chart(
            projection_3d_fig,
            use_container_width=True,
        )

    else:
        projection_3d_fig = plot_3d_projection_static(
            samples,
            x_param=x_param,
            y_param=y_param,
            z_param=z_param,
            cmap=plot_style.get("colormap", "viridis"),
            custom_colors=plot_style,
            qoi_min=qoi_min,
            qoi_max=qoi_max,
        )

        st.pyplot(projection_3d_fig)

    return projection_3d_fig


def display_parameter_report_export(
    metadata: dict,
    summary_df,
    intervals_df,
    samples,
    scatter_fig,
    projection_fig,
    projection_3d_fig,
    selected_projection_parameters,
    qoi_min: float,
    qoi_max: float,
) -> None:
    """
    Display controls for generating a parameter-analysis report.
    """
    st.subheader("Generate Parameter Analysis Report")

    output_root = st.text_input(
        "Report output folder",
        value="reports",
        key="parameter_analysis_report_output_folder",
    )

    figure_formats = st.multiselect(
        "Figure formats",
        ["png", "pdf", "jpg", "svg", "eps"],
        default=["png", "pdf"],
        key="parameter_analysis_report_figure_formats",
    )

    if not figure_formats:
        st.warning("Choose at least one figure format.")
        return

    if st.button(
        "Generate Parameter Analysis Report",
        key="generate_parameter_analysis_report",
        type="primary",
    ):
        report_metadata = metadata.copy()

        report_metadata.update({
            "qoi_color_min": qoi_min,
            "qoi_color_max": qoi_max,
            "selected_projection_parameters": list(
                selected_projection_parameters
            ),
        })

        report_dir = generate_parameter_analysis_report(
            output_root=output_root,
            metadata=report_metadata,
            qoi_summary_df=summary_df,
            prediction_intervals_df=intervals_df,
            samples=samples,
            scatter_fig=scatter_fig,
            projection_fig=projection_fig,
            projection_3d_fig=projection_3d_fig,
            figure_formats=figure_formats,
        )

        st.success(f"Saved report to: {report_dir}")

class SimpleComparisonRun:
    """
    Minimal run-like object for plot_qoi_multi_comparison().

    The existing plotting function expects each run to have:
    - label
    - method
    - samples
    """
    def __init__(self, label: str, method: str, samples: pd.DataFrame):
        self.label = label
        self.method = method
        self.samples = samples


def summarize_scenario_qoi(label: str, samples: pd.DataFrame) -> dict:
    """
    Summarize a scenario QoI distribution.
    """
    qoi = samples["QoI"]

    return {
        "scenario": label,
        "mean": qoi.mean(),
        "std": qoi.std(),
        "median": qoi.median(),
        "q025": qoi.quantile(0.025),
        "q975": qoi.quantile(0.975),
        "min": qoi.min(),
        "max": qoi.max(),
    }
"""
Dashboard UI for the Calibration tab.
"""

import pandas as pd
import streamlit as st

from uqdash.loader import load_model_from_path
from uqdash.calibration.core import (
    detect_observed_variables,
    run_least_squares_calibration,
    run_differential_evolution_calibration,
)
from uqdash.plots import (
    plot_calibration_fit,
    plot_residual_sequence,
    plot_residual_histogram,
)
from uqdash.reports.calibration_report import generate_calibration_report
from uqdash.dashboard.parameter_ordering import order_parameters_by_sobol

def display_calibration_tab(settings: dict) -> None:
    """
    Display the full calibration workflow.
    """
    st.header("Calibration")

    st.write(
        "Estimate model parameters by fitting model predictions to one or more "
        "observed variables."
    )

    display_calibration_help()

    model_module = load_model_from_path(settings["model_path"])
    parameter_names = order_parameters_by_sobol(
    list(model_module.PARAMETERS.keys())
)

    uploaded_file = st.file_uploader(
        "Upload calibration data CSV",
        type=["csv"],
        key="calibration_data_upload",
    )

    if uploaded_file is None:
        st.info("Upload a CSV file to begin calibration.")
        return

    data = pd.read_csv(uploaded_file)

    st.subheader("Calibration Data Preview")
    st.dataframe(data.head(), use_container_width=True, hide_index=True)

    observed_variables = detect_observed_variables(data)

    if not observed_variables:
        st.error(
            "No observed variables found. Use columns like "
            "`observed_TNBC`, `observed_M2`, or `observed_Tc`."
        )
        return

    selected_variables = st.multiselect(
        "Variables to fit",
        observed_variables,
        default=observed_variables,
        key="calibration_selected_variables",
    )

    if not selected_variables:
        st.warning("Choose at least one observed variable to fit.")
        return

    variable_weights = display_weight_controls(
        data=data,
        selected_variables=selected_variables,
    )

    parameters_to_estimate = st.multiselect(
        "Parameters to estimate",
        parameter_names,
        default=parameter_names[: min(2, len(parameter_names))],
        key="calibration_parameters_to_estimate",
    )

    if not parameters_to_estimate:
        st.warning("Choose at least one parameter to estimate.")
        return

    estimation_method = st.selectbox(
        "Parameter fitting method",
        ["Least Squares", "Differential Evolution"],
        key="calibration_estimation_method",
    )

    if st.button(
        "Run Calibration",
        key="run_calibration",
        type="primary",
    ):
        run_calibration(
            model_module=model_module,
            data=data,
            parameters_to_estimate=parameters_to_estimate,
            selected_variables=selected_variables,
            variable_weights=variable_weights,
            estimation_method=estimation_method,
            seed=settings.get("seed", 1),
            model_path=settings.get("model_path", ""),
        )

    if "calibration_result" in st.session_state:
        display_calibration_results(
            st.session_state["calibration_result"]
        )


def display_calibration_help() -> None:
    """
    Explain the expected calibration data format.
    """
    with st.expander("What should my calibration CSV look like?"):
        st.write(
            "Use one row per time point and columns named `observed_<state>` "
            "for each measured model variable."
        )

        example_df = pd.DataFrame({
            "time": [0, 24, 48, 72],
            "observed_TNBC": [2090, 2550, 3210, 4100],
            "observed_Tc": [66800, 64000, 61000, 57000],
            "observed_Treg": [10900, 11400, 11950, 12600],
        })

        st.dataframe(
            example_df,
            use_container_width=True,
            hide_index=True,
        )


def display_weight_controls(data, selected_variables):
    """
    Let the user choose how each variable contributes to the objective.
    """
    st.subheader("Variable Weights")

    weighting_method = st.selectbox(
        "Weighting method",
        [
            "Equal weights",
            "Normalize by max observed value",
            "Manual weights",
        ],
        key="calibration_weighting_method",
    )

    weights = {}

    if weighting_method == "Equal weights":
        for variable in selected_variables:
            weights[variable] = 1.0

    elif weighting_method == "Normalize by max observed value":
        for variable in selected_variables:
            observed = data[f"observed_{variable}"].abs()
            scale = float(observed.max())
            weights[variable] = 1.0 / scale if scale > 0 else 1.0

        st.write("Using weight = 1 / max(abs(observed variable)).")

    else:
        for variable in selected_variables:
            weights[variable] = st.number_input(
                f"Weight for {variable}",
                min_value=0.0,
                value=1.0,
                step=0.1,
                key=f"calibration_weight_{variable}",
            )

    weight_df = pd.DataFrame({
        "variable": list(weights.keys()),
        "weight": list(weights.values()),
    })

    st.dataframe(
        weight_df,
        use_container_width=True,
        hide_index=True,
    )

    return weights


def run_calibration(
    model_module,
    data,
    parameters_to_estimate,
    selected_variables,
    variable_weights,
    estimation_method,
    seed,
    model_path,
) -> None:
    """
    Run the selected calibration method.
    """
    try:
        with st.spinner("Running calibration..."):
            if estimation_method == "Least Squares":
                calibration_result = run_least_squares_calibration(
                    model_module=model_module,
                    data=data,
                    parameters_to_estimate=parameters_to_estimate,
                    selected_variables=selected_variables,
                    variable_weights=variable_weights,
                )

            elif estimation_method == "Differential Evolution":
                calibration_result = run_differential_evolution_calibration(
                    model_module=model_module,
                    data=data,
                    parameters_to_estimate=parameters_to_estimate,
                    selected_variables=selected_variables,
                    variable_weights=variable_weights,
                    seed=seed,
                )

            else:
                raise ValueError(
                    f"Unsupported parameter fitting method: {estimation_method}"
                )

        st.session_state["calibration_result"] = calibration_result
        st.session_state["calibration_data"] = data
        st.session_state["calibration_metadata"] = {
            "model_path": model_path,
            "estimation_method": estimation_method,
            "parameters_to_estimate": list(parameters_to_estimate),
            "selected_variables": list(selected_variables),
            "variable_weights": dict(variable_weights),
            "n_observations": len(data),
            "seed": seed,
        }

        st.success("Finished calibration!")

    except Exception as e:
        st.error(f"Error: {e}")


def display_calibration_results(calibration_result) -> None:
    """
    Display calibration results.
    """
    plot_style = st.session_state.get("plot_style", {})

    st.subheader("Calibration Summary")
    st.dataframe(
        calibration_result["summary"],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Variable-Level Fit Metrics")
    st.dataframe(
        calibration_result["variable_summary"],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Estimated Parameters")
    st.dataframe(
        calibration_result["fitted_parameters"],
        use_container_width=True,
        hide_index=True,
    )

    fit_df = calibration_result["fit_table"]
    selected_variables = calibration_result["selected_variables"]

    st.subheader("Calibration Fit")
    fit_fig = plot_calibration_fit(
        fit_df,
        selected_variables=selected_variables,
        colormap=plot_style.get("colormap", "viridis"),
        custom_colors=plot_style,
    )
    st.pyplot(fit_fig)

    st.subheader("Residual Diagnostics")
    residual_sequence_fig = plot_residual_sequence(
        fit_df,
        selected_variables=selected_variables,
        colormap=plot_style.get("colormap", "viridis"),
        custom_colors=plot_style,
    )
    residual_histogram_fig = plot_residual_histogram(
        fit_df,
        bar_color=plot_style.get("bar_color", "royalblue"),
        bar_alpha=plot_style.get("bar_alpha", 0.75),
    )

    st.pyplot(residual_sequence_fig)
    st.pyplot(residual_histogram_fig)

    st.divider()

    display_calibration_report_export(
        calibration_result=calibration_result,
        fit_fig=fit_fig,
        residual_sequence_fig=residual_sequence_fig,
        residual_histogram_fig=residual_histogram_fig,
    )

    st.subheader("Fit Table")
    st.dataframe(
        fit_df,
        use_container_width=True,
        hide_index=True,
    )


def display_calibration_report_export(
    calibration_result,
    fit_fig,
    residual_sequence_fig,
    residual_histogram_fig,
) -> None:
    """
    Display controls for generating a calibration report.
    """
    st.subheader("Generate Calibration Report")

    output_root = st.text_input(
        "Report output folder",
        value="reports",
        key="calibration_report_output_folder",
    )

    figure_formats = st.multiselect(
        "Figure formats",
        ["png", "pdf", "jpg", "svg", "eps"],
        default=["png", "pdf"],
        key="calibration_report_figure_formats",
    )

    if not figure_formats:
        st.warning("Choose at least one figure format.")
        return

    if st.button(
        "Generate Calibration Report",
        key="generate_calibration_report",
        type="primary",
    ):
        report_dir = generate_calibration_report(
            output_root=output_root,
            calibration_result=calibration_result,
            calibration_metadata=st.session_state.get("calibration_metadata", {}),
            fit_fig=fit_fig,
            residual_sequence_fig=residual_sequence_fig,
            residual_histogram_fig=residual_histogram_fig,
            figure_formats=figure_formats,
        )

        st.success(f"Saved report to: {report_dir}")
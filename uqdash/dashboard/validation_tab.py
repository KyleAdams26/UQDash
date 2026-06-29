"""
Dashboard UI for the Validation tab.

Validation checks whether model predictions agree with observed data.
"""

import pandas as pd
import streamlit as st

from uqdash.loader import load_model_from_path
from uqdash.validation.core import (
    get_nominal_params,
    run_validation,
)
from uqdash.plots import (
    plot_observed_vs_predicted,
    plot_validation_fit,
    plot_validation_residuals,
)
from uqdash.plots.common import get_two_plot_colors


def display_validation_tab(settings: dict) -> None:
    """
    Display the validation workflow.
    """
    st.header("Validation")

    st.write(
        "Validate model predictions by comparing them against observed data."
    )

    display_validation_help()

    model_module = load_model_from_path(settings["model_path"])

    uploaded_file = st.file_uploader(
        "Upload validation data CSV",
        type=["csv"],
        key="validation_data_upload",
    )

    if uploaded_file is None:
        st.info("Upload a CSV file to begin validation.")
        return

    data = pd.read_csv(uploaded_file)

    st.subheader("Validation Data Preview")
    st.dataframe(data.head(), use_container_width=True, hide_index=True)

    params = select_validation_parameters(model_module)

    if st.button(
        "Run Validation",
        key="run_validation",
        type="primary",
    ):
        try:
            with st.spinner("Running validation..."):
                validation_result = run_validation(
                    model_module=model_module,
                    data=data,
                    params=params,
                )

            st.session_state["validation_result"] = validation_result
            st.session_state["validation_data"] = data
            st.session_state["validation_metadata"] = {
                "model_path": settings["model_path"],
                "n_observations": len(data),
                "parameter_source": st.session_state.get(
                    "validation_parameter_source",
                    "Nominal parameters",
                ),
            }

            st.success("Finished validation!")

        except Exception as e:
            st.error(f"Error: {e}")

    if "validation_result" in st.session_state:
        display_validation_results(st.session_state["validation_result"])


def display_validation_help() -> None:
    """
    Explain the expected validation data format.
    """
    with st.expander("What should my validation CSV look like?"):
        st.write(
            "Validation checks whether model predictions agree with observed data."
        )

        st.write(
            "Your CSV should contain an observed output column. UQDash currently "
            "recognizes `observed`, `observed_qoi`, or `observed_population`."
        )

        example_df = pd.DataFrame({
            "time": [0, 1, 2, 3],
            "observed_population": [50.4, 66.8, 88.9, 116.1],
        })

        st.dataframe(
            example_df,
            use_container_width=True,
            hide_index=True,
        )

        st.write(
            "For time-series models, your model should define either "
            "`validation_predictions(params, data)` or "
            "`calibration_residuals(params, data)`."
        )


def select_validation_parameters(model_module):
    """
    Choose which parameter set should be used for validation.

    Supports:
    - nominal model parameters
    - latest UQDash calibrated parameters
    - manually entered external parameter values
    """
    options = ["Nominal parameters"]

    if (
        "calibration_result" in st.session_state
        and "calibrated_params" in st.session_state["calibration_result"]
    ):
        options.insert(0, "Latest calibrated parameters")

    options.append("Manual parameter values")

    parameter_source = st.radio(
        "Parameters to validate",
        options,
        key="validation_parameter_source",
    )

    if parameter_source == "Latest calibrated parameters":
        return st.session_state["calibration_result"]["calibrated_params"]

    if parameter_source == "Manual parameter values":
        return enter_manual_validation_parameters(model_module)

    return get_nominal_params(model_module)


def enter_manual_validation_parameters(model_module):
    """
    Let the user manually enter parameter values for validation.

    This is useful when parameters were estimated outside UQDash using a
    third-party optimizer, MCMC workflow, Bayesian method, or other tool.
    """
    st.write(
        "Enter the parameter values you want to validate. Defaults are filled "
        "using the model's nominal parameter values."
    )

    nominal_params = get_nominal_params(model_module)
    manual_params = {}

    for parameter, nominal_value in nominal_params.items():
        manual_params[parameter] = st.number_input(
            parameter,
            value=float(nominal_value),
            key=f"validation_manual_parameter_{parameter}",
        )

    return manual_params


def display_validation_results(validation_result) -> None:
    """
    Display validation metrics, plots, and validation data table.
    """
    plot_style = st.session_state.get("plot_style", {})
    observed_color, model_color = get_two_plot_colors(plot_style)

    st.subheader("Validation Metrics")
    st.dataframe(
        validation_result["summary"],
        use_container_width=True,
        hide_index=True,
    )

    validation_df = validation_result["validation_data"]

    st.subheader("Validation Fit")

    fit_fig = plot_validation_fit(
        validation_df,
        data_color=observed_color,
        fit_color=model_color,
        alpha=plot_style.get("bar_alpha", 0.85),
    )

    st.pyplot(fit_fig)

    st.subheader("Observed vs Predicted")

    observed_predicted_fig = plot_observed_vs_predicted(
        validation_df,
        point_color=observed_color,
        alpha=plot_style.get("bar_alpha", 0.75),
    )

    st.pyplot(observed_predicted_fig)

    st.subheader("Residuals")

    residual_fig = plot_validation_residuals(
        validation_df,
        point_color=observed_color,
        alpha=plot_style.get("bar_alpha", 0.75),
    )

    st.pyplot(residual_fig)

    st.subheader("Validation Table")
    st.dataframe(
        validation_df,
        use_container_width=True,
        hide_index=True,
    )
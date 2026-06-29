"""
Utilities for ordering parameter lists in dashboard controls.
"""

import streamlit as st


def order_parameters_by_sobol(parameter_names):
    """
    Return parameters ordered by descending Sobol total-order index if a
    Sobol run exists in session state. Otherwise return the original order.
    """
    if "sobol_run" not in st.session_state:
        return parameter_names

    sobol_run = st.session_state["sobol_run"]

    if not hasattr(sobol_run, "results"):
        return parameter_names

    results = sobol_run.results

    if "parameter" not in results.columns or "ST" not in results.columns:
        return parameter_names

    ranked_parameters = (
        results
        .sort_values("ST", ascending=False)["parameter"]
        .tolist()
    )

    # Keep only parameters present in the current model.
    ranked_parameters = [
        parameter for parameter in ranked_parameters
        if parameter in parameter_names
    ]

    # Add any parameters not included in the Sobol result.
    remaining_parameters = [
        parameter for parameter in parameter_names
        if parameter not in ranked_parameters
    ]

    return ranked_parameters + remaining_parameters
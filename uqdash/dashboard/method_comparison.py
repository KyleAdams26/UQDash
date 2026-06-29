"""
Dashboard UI for comparing compatible sensitivity-analysis methods.
"""

import streamlit as st

from uqdash.loader import load_model_from_path
from uqdash.comparison import run_comparison
from uqdash.plots import plot_method_comparison_bar


def display_method_comparison_section(settings: dict) -> None:
    """
    Display method-comparison workflow.

    For now, this compares methods that share a total-order index ST.
    Sobol and eFAST both support this. Morris is excluded because its main
    metric is mu_star, which is not the same as ST.
    """
    st.subheader("Method Comparison")

    st.write(
        "Compare compatible methods using total-order sensitivity indices. "
        "Currently this supports Sobol and eFAST."
    )

    selected_methods = st.multiselect(
        "Methods to compare",
        ["Sobol", "eFAST"],
        default=["Sobol", "eFAST"],
        key="method_comparison_selected_methods",
    )

    if st.button("Run Method Comparison", key="run_method_comparison_button"):
        run_method_comparison(settings, selected_methods)

    if "method_comparison_runs" in st.session_state:
        runs = st.session_state["method_comparison_runs"]

        st.pyplot(plot_method_comparison_bar(runs, metric="ST"))

        st.subheader("Comparison Table")
        st.dataframe(build_method_comparison_table(runs, metric="ST"))


def run_method_comparison(settings: dict, selected_methods: list[str]) -> None:
    """
    Run selected compatible sensitivity methods with all parameters varied.
    """
    if len(selected_methods) < 2:
        st.error("Choose at least two methods to compare.")
        return

    try:
        model_module = load_model_from_path(settings["model_path"])

        scenarios = [
            {
                "label": "All parameters varied",
                "frozen_parameters": [],
            }
        ]

        method_runs = []

        for method in selected_methods:
            with st.spinner(f"Running {method}..."):
                runs = run_comparison(
                    method=method,
                    model_module=model_module,
                    model_path=settings["model_path"],
                    scenarios=scenarios,
                    n_samples=settings["n_samples"],
                    seed=settings["seed"],
                )

            method_run = runs[0]

            if not method_run.supports_total_order_comparison():
                st.warning(
                    f"{method} does not produce ST values and was skipped."
                )
                continue

            method_runs.append(method_run)

        if len(method_runs) < 2:
            st.error("Need at least two compatible methods for comparison.")
            return

        st.session_state["method_comparison_runs"] = method_runs
        st.success("Finished method comparison!")

    except Exception as e:
        st.error(f"Error: {e}")


def build_method_comparison_table(runs, metric: str):
    """
    Build a wide comparison table with one column per method.
    """
    comparison_table = None

    for run in runs:
        method_table = run.results[["parameter", metric]].copy()
        method_table = method_table.rename(columns={metric: run.method})

        if comparison_table is None:
            comparison_table = method_table
        else:
            comparison_table = comparison_table.merge(
                method_table,
                on="parameter",
                how="outer",
            )

    return comparison_table
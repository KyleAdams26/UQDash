"""
Dashboard UI for the Model Simulation tab.
"""

import streamlit as st

from uqdash.loader import load_model_from_path
from uqdash.simulation.core import (
    get_nominal_params,
    run_model_simulation,
)
from uqdash.plots import plot_simulation_trajectories


def display_simulation_tab(settings: dict) -> None:
    """
    Display model simulation controls and results.
    """
    st.header("Model Simulation")

    st.write(
        "Simulate your model forward in time to inspect baseline dynamics "
        "before running sensitivity, uncertainty, calibration, or validation analyses."
    )

    model_module = load_model_from_path(settings["model_path"])
    nominal_params = get_nominal_params(model_module)

    st.subheader("Simulation Settings")

    col1, col2 = st.columns(2)

    with col1:
        t_final = st.number_input(
            "Final time",
            min_value=0.1,
            value=30.0,
            step=1.0,
            key="simulation_t_final",
        )

    with col2:
        n_time_points = st.number_input(
            "Number of time points",
            min_value=10,
            max_value=5000,
            value=300,
            step=10,
            key="simulation_n_time_points",
        )

    method = st.selectbox(
        "ODE solver method",
        ["RK45", "RK23", "DOP853", "Radau", "BDF", "LSODA"],
        key="simulation_solver_method",
    )

    st.subheader("Parameter Values")

    params = {}

    with st.expander("Edit simulation parameters", expanded=False):
        for parameter, nominal_value in nominal_params.items():
            params[parameter] = st.number_input(
                parameter,
                value=float(nominal_value),
                key=f"simulation_parameter_{parameter}",
            )

    if st.button(
        "Run Simulation",
        key="run_model_simulation",
        type="primary",
    ):
        run_simulation(
            model_module=model_module,
            params=params,
            t_final=t_final,
            n_time_points=n_time_points,
            method=method,
            model_path=settings["model_path"],
        )

    if "simulation_df" in st.session_state:
        display_simulation_results(st.session_state["simulation_df"])


def run_simulation(
    model_module,
    params: dict,
    t_final: float,
    n_time_points: int,
    method: str,
    model_path: str,
) -> None:
    """
    Run the model simulation and store results in session state.
    """
    try:
        with st.spinner("Running model simulation..."):
            simulation_df = run_model_simulation(
                model_module=model_module,
                params=params,
                t_final=t_final,
                n_time_points=n_time_points,
                method=method,
            )

        st.session_state["simulation_df"] = simulation_df
        st.session_state["simulation_metadata"] = {
            "model_path": model_path,
            "t_final": t_final,
            "n_time_points": n_time_points,
            "method": method,
            "params": params,
        }

        st.success("Finished simulation!")

    except Exception as e:
        st.error(f"Error: {e}")


def display_simulation_results(simulation_df) -> None:
    """
    Display simulation figures and data.
    """
    plot_style = st.session_state.get("plot_style", {})

    state_columns = [
        column for column in simulation_df.columns
        if column != "time"
    ]

    selected_states = st.multiselect(
        "States to display",
        state_columns,
        default=state_columns,
        key="simulation_selected_states",
    )

    if not selected_states:
        st.warning("Choose at least one state to display.")
        return

    fig = plot_simulation_trajectories(
        simulation_df,
        selected_states=selected_states,
        colormap=plot_style.get("colormap", "viridis"),
        custom_colors=plot_style,
        plot_style=plot_style,
    )

    st.pyplot(fig)

    st.subheader("Simulation Table")
    st.dataframe(
        simulation_df,
        use_container_width=True,
        hide_index=True,
    )
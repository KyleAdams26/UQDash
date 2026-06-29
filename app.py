import streamlit as st

from uqdash.dashboard.sidebar import display_sidebar
from uqdash.dashboard.sensitivity_tab import display_sensitivity_tab
from uqdash.dashboard.parameter_tab import display_parameter_tab
from uqdash.dashboard.uncertainty_tab import display_uncertainty_tab
from uqdash.dashboard.project_dashboard import display_project_dashboard
from uqdash.dashboard.calibration_tab import display_calibration_tab
from uqdash.dashboard.validation_tab import display_validation_tab
from uqdash.dashboard.simulation_tab import display_simulation_tab

st.title("UQdash")
st.subheader("Uncertainty Quantification and Parameter Analysis Dashboard")


# Collect global settings from the sidebar.
settings = display_sidebar()


# Build main dashboard tabs.
project_tab, simulation_tab, sensitivity_tab, parameter_tab, uncertainty_tab, calibration_tab, validation_tab = st.tabs([
    "Project Dashboard",
    "Model Simulation",
    "Sensitivity Analysis",
    "Parameter Analysis",
    "Uncertainty Propagation",
    "Calibration",
    "Validation",
])

with simulation_tab:
    display_simulation_tab(settings)

with project_tab:
    display_project_dashboard(settings)

with sensitivity_tab:
    display_sensitivity_tab(settings)

with parameter_tab:
    display_parameter_tab(settings)

with uncertainty_tab:
    display_uncertainty_tab(settings)

with calibration_tab:
    display_calibration_tab(settings)

with validation_tab:
    display_validation_tab(settings)
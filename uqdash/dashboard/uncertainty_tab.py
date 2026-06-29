"""
Dashboard UI for the Uncertainty Propagation tab.
"""

import streamlit as st

from uqdash.dashboard.uncertainty import display_uncertainty_propagation


def display_uncertainty_tab(settings: dict) -> None:
    """
    Display uncertainty propagation tools.
    """
    st.header("Uncertainty Propagation")

    display_uncertainty_propagation(settings)
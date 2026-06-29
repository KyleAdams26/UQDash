"""
Dashboard UI for displaying model parameter information.
"""

import pandas as pd
import streamlit as st


def parameter_info_to_dataframe(parameter_info: dict) -> pd.DataFrame:
    """
    Convert model PARAMETERS dictionary into a clean display table.
    """
    rows = []

    for name, info in parameter_info.items():
        bounds = info.get("bounds", [None, None])

        rows.append({
            "Parameter": name,
            "Lower bound": bounds[0],
            "Upper bound": bounds[1],
            "Nominal": info.get("nominal", None),
        })

    return pd.DataFrame(rows)


def display_parameter_summary(parameter_info: dict) -> None:
    """
    Display parameter information in a polished, compact format.
    """
    parameter_df = parameter_info_to_dataframe(parameter_info)

    st.subheader("Model Parameters")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Number of parameters", len(parameter_df))

    with col2:
        num_nominal = parameter_df["Nominal"].notna().sum()
        st.metric("Nominal values provided", num_nominal)

    st.dataframe(
        parameter_df,
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Raw parameter specification"):
        st.json(parameter_info)
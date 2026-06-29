"""
Project Dashboard tab.

This tab summarizes the current UQDash session. It does not run new analyses.
Instead, it gives the user a quick overview of what has already been computed.
"""

import streamlit as st


def display_project_dashboard(settings: dict) -> None:
    """
    Display a high-level summary of the current UQDash project/session.
    """
    st.header("Project Dashboard")

    st.write(
        "This page summarizes the model, completed analyses, and key results "
        "from the current UQDash session."
    )

    display_model_overview(settings)

    st.divider()
    display_completed_analysis_overview()

    st.divider()
    display_latest_sensitivity_summary()

    st.divider()
    display_latest_uncertainty_summary()

    st.divider()
    display_latest_parameter_analysis_summary()


def display_model_overview(settings: dict) -> None:
    """
    Display basic model and run settings.
    """
    st.subheader("Model Overview")

    st.write(f"**Model path:** `{settings.get('model_path', 'Not selected')}`")
    st.write(f"**Default sample size:** {settings.get('n_samples', 'Not set')}")
    st.write(f"**Default seed:** {settings.get('seed', 'Not set')}")


def display_completed_analysis_overview() -> None:
    """
    Show which major analyses have been completed in this session.
    """
    st.subheader("Completed Analyses")

    completed = {
        "Sensitivity analysis": "sensitivity_run" in st.session_state,
        "Parameter analysis": "parameter_analysis_samples" in st.session_state,
        "Uncertainty propagation": "uncertainty_samples" in st.session_state,
        "Method comparison": "method_comparison_runs" in st.session_state,
        "Convergence diagnostic": "convergence_df" in st.session_state,
    }

    for name, is_done in completed.items():
        if is_done:
            st.success(f"{name}: complete")
        else:
            st.info(f"{name}: not run yet")


def display_latest_sensitivity_summary() -> None:
    """
    Summarize the latest sensitivity-analysis run.
    """
    st.subheader("Latest Sensitivity Summary")

    if "sensitivity_run" not in st.session_state:
        st.info("No sensitivity analysis has been run yet.")
        return

    run = st.session_state["sensitivity_run"]
    main_metric = run.main_metric()

    ranked_results = run.results.sort_values(
        main_metric,
        ascending=False,
    )

    top_parameter = ranked_results.iloc[0]["parameter"]
    top_value = ranked_results.iloc[0][main_metric]

    st.write(f"**Method:** {run.method}")
    st.write(f"**Base sample size:** {run.n_samples}")
    st.write(f"**Seed:** {run.seed}")
    st.write(f"**Main ranking metric:** `{main_metric}`")
    st.metric("Top-ranked parameter", top_parameter)
    st.metric(f"Top {main_metric}", f"{top_value:.4g}")

    st.dataframe(
        ranked_results.head(10),
        use_container_width=True,
        hide_index=True,
    )


def display_latest_uncertainty_summary() -> None:
    """
    Summarize the latest uncertainty-propagation run.
    """
    st.subheader("Latest Uncertainty Summary")

    if "uncertainty_samples" not in st.session_state:
        st.info("No uncertainty propagation run has been completed yet.")
        return

    samples = st.session_state["uncertainty_samples"]
    metadata = st.session_state.get("uncertainty_metadata", {})
    qoi = samples["QoI"]

    st.write(f"**Sampler:** {metadata.get('sampler', 'Unknown')}")
    st.write(f"**Distribution:** {metadata.get('distribution', 'Uniform')}")
    st.write(f"**Sample size:** {metadata.get('n_samples', len(samples))}")
    st.write(f"**Seed:** {metadata.get('seed', 'Unknown')}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Mean QoI", f"{qoi.mean():.4g}")

    with col2:
        st.metric("Median QoI", f"{qoi.median():.4g}")

    with col3:
        st.metric("Std QoI", f"{qoi.std():.4g}")


def display_latest_parameter_analysis_summary() -> None:
    """
    Summarize the latest parameter-analysis run.
    """
    st.subheader("Latest Parameter Analysis Summary")

    if "parameter_analysis_samples" not in st.session_state:
        st.info("No parameter analysis run has been completed yet.")
        return

    samples = st.session_state["parameter_analysis_samples"]
    metadata = st.session_state.get("parameter_analysis_metadata", {})

    parameter_names = [
        column for column in samples.columns
        if column != "QoI"
    ]

    correlations = []

    for parameter in parameter_names:
        correlations.append({
            "parameter": parameter,
            "spearman_corr": samples[parameter].corr(
                samples["QoI"],
                method="spearman",
            ),
        })

    import pandas as pd

    correlation_df = pd.DataFrame(correlations)
    correlation_df["abs_spearman_corr"] = correlation_df["spearman_corr"].abs()
    correlation_df = correlation_df.sort_values(
        "abs_spearman_corr",
        ascending=False,
    )

    st.write(f"**Sampler:** {metadata.get('sampler', 'Unknown')}")
    st.write(f"**Distribution:** {metadata.get('distribution', 'Uniform')}")
    st.write(f"**Sample size:** {metadata.get('n_samples', len(samples))}")
    st.write(f"**Seed:** {metadata.get('seed', 'Unknown')}")

    st.dataframe(
        correlation_df.head(10),
        use_container_width=True,
        hide_index=True,
    )
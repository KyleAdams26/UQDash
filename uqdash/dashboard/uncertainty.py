"""
Dashboard UI for uncertainty propagation.
"""

import streamlit as st

from uqdash.loader import load_model_from_path
from uqdash.uncertainty.sampling import (
    generate_uncertainty_samples,
    evaluate_uncertainty_samples,
)
from uqdash.uncertainty.propagation import (
    summarize_qoi_uncertainty,
    compute_prediction_intervals,
    compute_exceedance_probability,
    summarize_multiple_runs,
)
from uqdash.plots import (
    plot_uncertainty_histogram,
    plot_prediction_intervals,
    plot_exceedance_probability,
    plot_scenario_uncertainty_comparison,
)
from uqdash.reports.uncertainty_report import generate_uncertainty_report


def display_uncertainty_propagation(settings: dict) -> None:
    """
    Display scalar QoI uncertainty propagation.

    This workflow generates independent uncertainty-propagation samples.
    It does not reuse Sobol A/B/AB_i samples from sensitivity analysis.
    """
    st.subheader("Uncertainty Propagation")

    st.write(
        "Generate independent parameter samples and propagate them through "
        "the model to estimate uncertainty in the quantity of interest."
    )

    sampler = st.selectbox(
        "Sampling method",
        ["Sobol QMC", "Latin Hypercube", "Random Monte Carlo"],
        key="uncertainty_sampler",
    )
    st.subheader("Distribution Explorer")

    st.write(
        "Choose the probability distribution used to sample each parameter "
        "within its specified bounds."
    )

    # ------------------------------------------------------------
    # Choose the probability distribution used when sampling each
    # parameter within its specified bounds.
    # ------------------------------------------------------------
    distribution = st.selectbox(
        "Parameter distribution",
        [
            "Uniform",
            "Normal",
            "Lognormal",
            "Triangular",
        ],
        key="uncertainty_parameter_distribution",
    )

    sample_power = st.number_input(
        "Sample size as 2^k",
        min_value=4,
        max_value=20,
        value=10,
        step=1,
        key="uncertainty_sample_power",
    )

    n_samples = 2 ** sample_power

    seed = st.number_input(
        "Random seed",
        min_value=0,
        value=settings.get("seed", 1),
        step=1,
        key="uncertainty_seed",
    )

    st.write(f"Using uncertainty sample size: {n_samples}")

    if st.button("Run Uncertainty Propagation", key="run_uncertainty_propagation"):
        run_uncertainty_propagation(
            settings=settings,
            sampler=sampler,
            distribution=distribution,
            n_samples=n_samples,
            seed=seed,
        )

    if "uncertainty_samples" not in st.session_state:
        st.info("Run uncertainty propagation to view QoI uncertainty summaries.")
        return

    display_uncertainty_results(st.session_state["uncertainty_samples"])


def run_uncertainty_propagation(
    settings: dict,
    sampler: str,
    n_samples: int,
    seed: int,
    distribution: str,
) -> None:
    """
    Generate independent uncertainty samples and evaluate the model.
    """
    try:
        model_module = load_model_from_path(settings["model_path"])

        with st.spinner("Generating uncertainty samples..."):
            parameter_samples = generate_uncertainty_samples(
                model_module=model_module,
                n_samples=n_samples,
                seed=seed,
                distribution=distribution,
                sampler=sampler,
            )

        with st.spinner("Evaluating model on uncertainty samples..."):
            uncertainty_samples = evaluate_uncertainty_samples(
                model_module=model_module,
                parameter_samples=parameter_samples,
            )

        st.session_state["uncertainty_samples"] = uncertainty_samples
        st.session_state["uncertainty_metadata"] = {
            "model_path": settings["model_path"],
            "sampler": sampler,
            "distribution": distribution,
            "n_samples": n_samples,
            "seed": seed,
        }

        st.success("Finished uncertainty propagation!")

    except Exception as e:
        st.error(f"Error: {e}")


def display_uncertainty_results(uncertainty_samples) -> None:
    """
    Display uncertainty propagation results and report export controls.
    """
    plot_style = st.session_state.get("plot_style", {})
    metadata = st.session_state.get("uncertainty_metadata", {})

    st.write(f"Sampling method: {metadata.get('sampler')}")
    st.write(f"Sample size: {metadata.get('n_samples')}")
    st.write(f"Seed: {metadata.get('seed')}")

    bins = st.slider(
        "Histogram bins",
        min_value=10,
        max_value=100,
        value=40,
        step=5,
        key="uncertainty_histogram_bins",
    )

    summary_df = summarize_qoi_uncertainty(uncertainty_samples)
    intervals_df = compute_prediction_intervals(uncertainty_samples)

    histogram_fig = plot_uncertainty_histogram(
        uncertainty_samples,
        bins=bins,
        bar_color=plot_style.get("bar_color", "royalblue"),
        bar_alpha=plot_style.get("bar_alpha", 0.75),
    )

    intervals_fig = plot_prediction_intervals(intervals_df)

    st.pyplot(histogram_fig)

    st.subheader("QoI Summary Statistics")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Prediction Intervals")
    st.pyplot(intervals_fig)
    st.dataframe(intervals_df, use_container_width=True, hide_index=True)

    st.divider()

    exceedance_df, exceedance_fig, threshold, direction = display_exceedance_view(
        uncertainty_samples
    )

    st.divider()

    scenario_summary_df, scenario_fig = display_scenario_uncertainty_comparison()

    st.divider()

    display_uncertainty_report_export(
        metadata=metadata,
        bins=bins,
        summary_df=summary_df,
        intervals_df=intervals_df,
        exceedance_df=exceedance_df,
        exceedance_fig=exceedance_fig,
        histogram_fig=histogram_fig,
        intervals_fig=intervals_fig,
        threshold=threshold,
        direction=direction,
        scenario_summary_df=scenario_summary_df,
        scenario_fig=scenario_fig,
    )


def display_exceedance_view(uncertainty_samples):
    """
    Display exceedance probability controls and plot.

    Returns:
        exceedance_df, exceedance_fig, threshold, direction
    """
    st.subheader("Threshold View")

    st.write(
        "Estimate the probability that the QoI is above or below a chosen threshold."
    )

    plot_style = st.session_state.get("plot_style", {})
    qoi = uncertainty_samples["QoI"]

    default_threshold = float(qoi.median())

    col1, col2 = st.columns(2)

    with col1:
        threshold = st.number_input(
            "Threshold",
            value=default_threshold,
            key="exceedance_threshold",
        )

    with col2:
        direction = st.selectbox(
            "Event direction",
            ["Above", "Below"],
            key="exceedance_direction",
        )

    exceedance_df = compute_exceedance_probability(
        uncertainty_samples,
        threshold=threshold,
        direction=direction,
    )

    probability = exceedance_df["percent"].iloc[0]

    st.metric("Estimated probability", f"{probability:.2f}%")

    exceedance_fig = plot_exceedance_probability(
        exceedance_df,
        bar_color=plot_style.get("bar_color", "royalblue"),
        bar_alpha=plot_style.get("bar_alpha", 0.85),
    )

    st.pyplot(exceedance_fig)
    st.dataframe(exceedance_df, use_container_width=True, hide_index=True)

    return exceedance_df, exceedance_fig, threshold, direction


def display_scenario_uncertainty_comparison():
    """
    Display scenario uncertainty comparison.

    Returns:
        scenario_summary_df, scenario_fig

    If no comparison runs exist, both are returned as None.
    """
    st.subheader("Scenario Uncertainty Comparison")

    if "comparison_runs" not in st.session_state:
        st.info(
            "Run a Parameter Comparison to compare uncertainty across scenarios. "
            "The current uncertainty run is shown in the histogram and intervals above."
        )
        return None, None

    available_runs = st.session_state["comparison_runs"]

    st.write(
        "Comparing propagated QoI uncertainty across parameter-analysis scenarios."
    )

    scenario_summary_df = summarize_multiple_runs(available_runs)
    scenario_fig = plot_scenario_uncertainty_comparison(scenario_summary_df)

    st.pyplot(scenario_fig)
    st.dataframe(scenario_summary_df, use_container_width=True, hide_index=True)

    return scenario_summary_df, scenario_fig


def display_uncertainty_report_export(
    metadata: dict,
    bins: int,
    summary_df,
    intervals_df,
    exceedance_df,
    exceedance_fig,
    histogram_fig,
    intervals_fig,
    threshold: float,
    direction: str,
    scenario_summary_df=None,
    scenario_fig=None,
) -> None:
    """
    Display report export controls and generate report files.
    """
    st.subheader("Export Uncertainty Report")

    output_root = st.text_input(
        "Report output folder",
        value="reports",
        key="uncertainty_report_output_folder",
    )

    figure_formats = st.multiselect(
        "Figure formats",
        ["png", "pdf", "jpg", "svg", "eps"],
        default=["png", "pdf"],
        key="uncertainty_report_figure_formats",
    )

    if not figure_formats:
        st.warning("Choose at least one figure format.")
        return

    if st.button("Generate Uncertainty Report", key="generate_uncertainty_report"):
        report_metadata = metadata.copy()

        report_metadata.update({
            "histogram_bins": bins,
            "exceedance_threshold": threshold,
            "exceedance_direction": direction,
            "exceedance_probability": float(exceedance_df["probability"].iloc[0]),
            "exceedance_percent": float(exceedance_df["percent"].iloc[0]),
        })

        report_dir = generate_uncertainty_report(
            output_root=output_root,
            metadata=report_metadata,
            histogram_bins=bins,
            summary_df=summary_df,
            intervals_df=intervals_df,
            exceedance_df=exceedance_df,
            histogram_fig=histogram_fig,
            intervals_fig=intervals_fig,
            exceedance_fig=exceedance_fig,
            scenario_summary_df=scenario_summary_df,
            scenario_fig=scenario_fig,
            figure_formats=figure_formats,
        )

        st.success(f"Saved report to: {report_dir}")
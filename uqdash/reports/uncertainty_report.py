"""
Report generation for uncertainty propagation.
"""

import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


def save_figure_all_formats(fig, output_dir: Path, base_name: str, formats: list[str]):
    """
    Save a Matplotlib figure in selected formats.
    """
    saved_paths = []

    for fmt in formats:
        file_path = output_dir / f"{base_name}.{fmt}"
        fig.savefig(file_path, bbox_inches="tight", dpi=300)
        saved_paths.append(str(file_path))

    return saved_paths


def generate_uncertainty_report(
    output_root: str,
    metadata: dict,
    histogram_bins: int,
    summary_df,
    intervals_df,
    exceedance_df,
    histogram_fig,
    intervals_fig,
    exceedance_fig,
    scenario_summary_df=None,
    scenario_fig=None,
    figure_formats=None,
):
    """
    Generate a report folder for uncertainty propagation.

    Saves:
        - metadata JSON
        - QoI summary statistics CSV
        - prediction intervals CSV
        - exceedance results CSV
        - figures in selected formats
        - optional scenario comparison outputs
    """
    if figure_formats is None:
        figure_formats = ["png", "pdf"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_dir = Path(output_root) / f"uncertainty_report_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_metadata = {
        **metadata,
        "histogram_bins": histogram_bins,
        "figure_formats": figure_formats,
        "created_at": timestamp,
    }

    with open(output_dir / "metadata.json", "w") as file:
        json.dump(report_metadata, file, indent=4)

    summary_df.to_csv(output_dir / "qoi_summary_statistics.csv", index=False)
    intervals_df.to_csv(output_dir / "prediction_intervals.csv", index=False)
    exceedance_df.to_csv(output_dir / "exceedance_probability.csv", index=False)

    save_figure_all_formats(
        histogram_fig,
        output_dir,
        "qoi_uncertainty_histogram",
        figure_formats,
    )

    save_figure_all_formats(
        intervals_fig,
        output_dir,
        "prediction_intervals",
        figure_formats,
    )

    save_figure_all_formats(
        exceedance_fig,
        output_dir,
        "exceedance_probability",
        figure_formats,
    )

    if scenario_summary_df is not None:
        scenario_summary_df.to_csv(
            output_dir / "scenario_uncertainty_comparison.csv",
            index=False,
        )

    if scenario_fig is not None:
        save_figure_all_formats(
            scenario_fig,
            output_dir,
            "scenario_uncertainty_comparison",
            figure_formats,
        )

    return output_dir
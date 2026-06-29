"""
Report generation for parameter analysis.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd


def generate_parameter_analysis_report(
    output_root: str,
    metadata: dict,
    samples: pd.DataFrame,
    qoi_summary_df: pd.DataFrame,
    parameter_summary_df: pd.DataFrame,
    correlation_df: pd.DataFrame,
    scatter_fig,
    projection_fig=None,
    projection_3d_fig=None,
    figure_formats=None,
) -> Path:
    """
    Save a parameter-analysis report folder.

    The report includes:
    - raw sample results
    - QoI summary statistics
    - parameter summary statistics
    - parameter-QoI correlations
    - selected figures
    - a Markdown summary report
    """
    if figure_formats is None:
        figure_formats = ["png", "pdf"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(output_root) / f"parameter_analysis_report_{timestamp}"
    figures_dir = report_dir / "figures"
    tables_dir = report_dir / "tables"

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    samples_path = tables_dir / "parameter_analysis_samples.csv"
    qoi_summary_path = tables_dir / "qoi_summary.csv"
    parameter_summary_path = tables_dir / "parameter_summary.csv"
    correlation_path = tables_dir / "parameter_qoi_correlations.csv"

    samples.to_csv(samples_path, index=False)
    qoi_summary_df.to_csv(qoi_summary_path, index=False)
    parameter_summary_df.to_csv(parameter_summary_path, index=False)
    correlation_df.to_csv(correlation_path, index=False)

    saved_figures = []

    saved_figures.extend(
        save_figure(
            scatter_fig,
            figures_dir,
            "single_parameter_scatter",
            figure_formats,
        )
    )

    if projection_fig is not None:
        saved_figures.extend(
            save_figure(
                projection_fig,
                figures_dir,
                "pairwise_projection_grid",
                figure_formats,
            )
        )
    
    if projection_3d_fig is not None:
        saved_figures.extend(
            save_figure(
                projection_3d_fig,
                figures_dir,
                "static_3d_projection",
                figure_formats,
            )
        )

    markdown_path = report_dir / "parameter_analysis_report.md"

    write_markdown_report(
        markdown_path=markdown_path,
        metadata=metadata,
        qoi_summary_df=qoi_summary_df,
        parameter_summary_df=parameter_summary_df,
        correlation_df=correlation_df,
        saved_figures=saved_figures,
    )

    return report_dir


def save_figure(fig, figures_dir: Path, stem: str, figure_formats):
    """
    Save a Matplotlib figure in one or more formats.
    """
    saved_paths = []

    for fmt in figure_formats:
        path = figures_dir / f"{stem}.{fmt}"
        fig.savefig(path, bbox_inches="tight", dpi=300)
        saved_paths.append(path)

    return saved_paths


def write_markdown_report(
    markdown_path: Path,
    metadata: dict,
    qoi_summary_df: pd.DataFrame,
    parameter_summary_df: pd.DataFrame,
    correlation_df: pd.DataFrame,
    saved_figures,
) -> None:
    """
    Write a Markdown summary report.
    """
    top_correlations = correlation_df.head(10)

    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write("# Parameter Analysis Report\n\n")

        f.write("## Run Metadata\n\n")
        for key, value in metadata.items():
            f.write(f"- **{key}:** {value}\n")

        f.write("\n## QoI Summary Statistics\n\n")
        f.write(qoi_summary_df.to_markdown(index=False))
        f.write("\n\n")

        f.write("## Top Parameter-QoI Correlations\n\n")
        f.write(top_correlations.to_markdown(index=False))
        f.write("\n\n")

        f.write("## Parameter Summary Statistics\n\n")
        f.write(
            "The full parameter summary table was saved as "
            "`tables/parameter_summary.csv`.\n\n"
        )

        f.write("## Saved Figures\n\n")
        if saved_figures:
            for path in saved_figures:
                relative_path = path.relative_to(markdown_path.parent)
                f.write(f"- `{relative_path}`\n")
        else:
            f.write("No figures were saved.\n")
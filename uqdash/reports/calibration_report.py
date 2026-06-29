"""
Report generation for calibration.
"""

import json
from datetime import datetime
from pathlib import Path


def generate_calibration_report(
    output_root: str,
    calibration_result,
    calibration_metadata: dict,
    fit_fig,
    residual_sequence_fig,
    residual_histogram_fig,
    figure_formats=None,
) -> Path:
    """
    Save a calibration report folder.
    """
    if figure_formats is None:
        figure_formats = ["png", "pdf"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_dir = Path(output_root) / f"calibration_report_{timestamp}"
    figures_dir = report_dir / "figures"
    tables_dir = report_dir / "tables"

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    calibration_result["summary"].to_csv(
        tables_dir / "calibration_summary.csv",
        index=False,
    )

    calibration_result["fitted_parameters"].to_csv(
        tables_dir / "estimated_parameters.csv",
        index=False,
    )

    calibration_result["residuals"].to_csv(
        tables_dir / "residuals.csv",
        index=False,
    )

    with open(report_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(calibration_metadata, f, indent=4)

    saved_figures = []

    saved_figures.extend(
        save_figure(fit_fig, figures_dir, "calibration_fit", figure_formats)
    )

    saved_figures.extend(
        save_figure(
            residual_sequence_fig,
            figures_dir,
            "residual_sequence",
            figure_formats,
        )
    )

    saved_figures.extend(
        save_figure(
            residual_histogram_fig,
            figures_dir,
            "residual_histogram",
            figure_formats,
        )
    )

    write_markdown_report(
        markdown_path=report_dir / "calibration_report.md",
        calibration_result=calibration_result,
        calibration_metadata=calibration_metadata,
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
    calibration_result,
    calibration_metadata: dict,
    saved_figures,
) -> None:
    """
    Write a Markdown calibration report.
    """
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write("# Calibration Report\n\n")

        f.write("## Metadata\n\n")
        for key, value in calibration_metadata.items():
            f.write(f"- **{key}:** {value}\n")

        f.write("\n## Calibration Summary\n\n")
        f.write(calibration_result["summary"].to_markdown(index=False))
        f.write("\n\n")

        f.write("## Estimated Parameters\n\n")
        f.write(calibration_result["fitted_parameters"].to_markdown(index=False))
        f.write("\n\n")

        f.write("## Saved Tables\n\n")
        f.write("- `tables/calibration_summary.csv`\n")
        f.write("- `tables/estimated_parameters.csv`\n")
        f.write("- `tables/residuals.csv`\n")
        f.write("- `metadata.json`\n\n")

        f.write("## Saved Figures\n\n")
        for path in saved_figures:
            relative_path = path.relative_to(markdown_path.parent)
            f.write(f"- `{relative_path}`\n")
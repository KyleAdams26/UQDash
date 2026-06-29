"""
Report generation for validation analyses.
"""

import json
from datetime import datetime
from pathlib import Path


def generate_validation_report(
    output_root: str,
    validation_result,
    validation_metadata: dict,
    fit_fig,
    observed_predicted_fig,
    residual_fig,
    figure_formats=None,
) -> Path:
    """
    Save a validation report folder.

    The report includes:
    - validation metric table
    - validation data table with predictions and residuals
    - metadata JSON
    - validation fit, observed-vs-predicted, and residual figures
    - Markdown summary report
    """
    if figure_formats is None:
        figure_formats = ["png", "pdf"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(output_root) / f"validation_report_{timestamp}"

    figures_dir = report_dir / "figures"
    tables_dir = report_dir / "tables"

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    validation_result["summary"].to_csv(
        tables_dir / "validation_metrics.csv",
        index=False,
    )

    validation_result["validation_data"].to_csv(
        tables_dir / "validation_predictions.csv",
        index=False,
    )

    with open(report_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(validation_metadata, f, indent=4)

    saved_figures = []

    saved_figures.extend(
        save_figure(
            fit_fig,
            figures_dir,
            "validation_fit",
            figure_formats,
        )
    )

    saved_figures.extend(
        save_figure(
            observed_predicted_fig,
            figures_dir,
            "observed_vs_predicted",
            figure_formats,
        )
    )

    saved_figures.extend(
        save_figure(
            residual_fig,
            figures_dir,
            "validation_residuals",
            figure_formats,
        )
    )

    write_markdown_report(
        markdown_path=report_dir / "validation_report.md",
        validation_result=validation_result,
        validation_metadata=validation_metadata,
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
    validation_result,
    validation_metadata: dict,
    saved_figures,
) -> None:
    """
    Write a Markdown validation report.
    """
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write("# Validation Report\n\n")

        f.write("## Metadata\n\n")
        if validation_metadata:
            for key, value in validation_metadata.items():
                f.write(f"- **{key}:** {value}\n")
        else:
            f.write("_No metadata available._\n")

        f.write("\n## Validation Metrics\n\n")
        f.write(validation_result["summary"].to_markdown(index=False))
        f.write("\n\n")

        f.write("## Saved Tables\n\n")
        f.write("- `tables/validation_metrics.csv`\n")
        f.write("- `tables/validation_predictions.csv`\n")
        f.write("- `metadata.json`\n\n")

        f.write("## Saved Figures\n\n")
        if saved_figures:
            for path in saved_figures:
                relative_path = path.relative_to(markdown_path.parent)
                f.write(f"- `{relative_path}`\n")
        else:
            f.write("_No figures saved._\n")
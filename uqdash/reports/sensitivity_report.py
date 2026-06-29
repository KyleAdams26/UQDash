"""
Report generation for sensitivity analysis.
"""

import json
from datetime import datetime
from pathlib import Path


def generate_sensitivity_report(
    output_root: str,
    run,
    sensitivity_fig,
    figure_formats=None,
) -> Path:
    """
    Save a sensitivity-analysis report folder.

    The report includes:
    - sensitivity index table
    - simulation samples
    - run metadata
    - sensitivity ranking figure
    - Markdown summary report
    """
    if figure_formats is None:
        figure_formats = ["png", "pdf"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_method = run.method.lower().replace(" ", "_")
    report_dir = Path(output_root) / f"sensitivity_report_{safe_method}_{timestamp}"

    figures_dir = report_dir / "figures"
    tables_dir = report_dir / "tables"

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    # Save core result tables.
    results_path = tables_dir / "sensitivity_results.csv"
    samples_path = tables_dir / "simulation_samples.csv"
    metadata_path = report_dir / "metadata.json"

    run.results.to_csv(results_path, index=False)
    run.samples.to_csv(samples_path, index=False)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(run.metadata(), f, indent=4)

    # Save ranking figure in each requested format.
    saved_figures = save_figure(
        fig=sensitivity_fig,
        figures_dir=figures_dir,
        stem="sensitivity_ranking",
        figure_formats=figure_formats,
    )

    markdown_path = report_dir / "sensitivity_report.md"

    write_markdown_report(
        markdown_path=markdown_path,
        run=run,
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
    run,
    saved_figures,
) -> None:
    """
    Write a Markdown report summarizing the sensitivity-analysis run.
    """
    main_metric = run.main_metric()

    ranked_results = run.results.sort_values(
        main_metric,
        ascending=False,
    )

    top_results = ranked_results.head(10)

    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write("# Sensitivity Analysis Report\n\n")

        f.write("## Run Metadata\n\n")
        f.write(f"- **Method:** {run.method}\n")
        f.write(f"- **Scenario:** {run.label}\n")
        f.write(f"- **Base sample size:** {run.n_samples}\n")
        f.write(f"- **Estimated model evaluations:** {run.estimated_runs}\n")
        f.write(f"- **Seed:** {run.seed}\n")
        f.write(f"- **Main ranking metric:** {main_metric}\n")

        f.write("\n## Top Sensitivity Rankings\n\n")
        f.write(top_results.to_markdown(index=False))
        f.write("\n\n")

        f.write("## Saved Tables\n\n")
        f.write("- `tables/sensitivity_results.csv`\n")
        f.write("- `tables/simulation_samples.csv`\n")
        f.write("- `metadata.json`\n\n")

        f.write("## Saved Figures\n\n")
        if saved_figures:
            for path in saved_figures:
                relative_path = path.relative_to(markdown_path.parent)
                f.write(f"- `{relative_path}`\n")
        else:
            f.write("No figures were saved.\n")
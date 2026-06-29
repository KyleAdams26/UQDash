"""
Convergence diagnostics for sensitivity-analysis methods.

These utilities rerun a sensitivity analysis at increasing sample sizes
and track how the main sensitivity metric changes.
"""

import pandas as pd

from uqdash.comparison import run_comparison


def run_convergence_diagnostic(
    method: str,
    model_module,
    model_path: str,
    sample_powers: list[int],
    seed: int,
):
    """
    Run the same sensitivity analysis across multiple sample sizes.

    Returns:
        convergence_df:
            Long-format dataframe with columns:
            sample_power, n_samples, parameter, metric, value
        runs:
            List of AnalysisRun objects, one for each sample size.
    """
    scenarios = [
        {
            "label": "All parameters varied",
            "frozen_parameters": [],
        }
    ]

    all_rows = []
    runs = []

    for sample_power in sample_powers:
        n_samples = 2 ** sample_power

        run = run_comparison(
            method=method,
            model_module=model_module,
            model_path=model_path,
            scenarios=scenarios,
            n_samples=n_samples,
            seed=seed,
        )[0]

        runs.append(run)

        metric = run.main_metric()

        for _, row in run.results.iterrows():
            all_rows.append({
                "sample_power": sample_power,
                "n_samples": n_samples,
                "parameter": row["parameter"],
                "metric": metric,
                "value": row[metric],
                "method": method,
            })

    convergence_df = pd.DataFrame(all_rows)

    return convergence_df, runs
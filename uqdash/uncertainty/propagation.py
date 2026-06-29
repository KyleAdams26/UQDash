"""
Uncertainty propagation utilities.

These functions summarize the uncertainty in model outputs induced by
uncertainty in sampled model parameters.
"""

import pandas as pd


def summarize_qoi_uncertainty(samples: pd.DataFrame, qoi_column: str = "QoI") -> pd.DataFrame:
    """
    Compute summary statistics for a scalar QoI distribution.
    """
    qoi = samples[qoi_column]

    summary = {
        "mean": qoi.mean(),
        "std": qoi.std(),
        "min": qoi.min(),
        "q025": qoi.quantile(0.025),
        "q05": qoi.quantile(0.05),
        "median": qoi.median(),
        "q95": qoi.quantile(0.95),
        "q975": qoi.quantile(0.975),
        "max": qoi.max(),
    }

    return pd.DataFrame([summary])


def compute_prediction_intervals(samples: pd.DataFrame, qoi_column: str = "QoI") -> pd.DataFrame:
    """
    Compute common prediction intervals for the QoI distribution.
    """
    qoi = samples[qoi_column]

    intervals = [
        {
            "interval": "50%",
            "lower": qoi.quantile(0.25),
            "upper": qoi.quantile(0.75),
        },
        {
            "interval": "90%",
            "lower": qoi.quantile(0.05),
            "upper": qoi.quantile(0.95),
        },
        {
            "interval": "95%",
            "lower": qoi.quantile(0.025),
            "upper": qoi.quantile(0.975),
        },
    ]

    return pd.DataFrame(intervals)

def compute_exceedance_probability(
    samples: pd.DataFrame,
    threshold: float,
    qoi_column: str = "QoI",
    direction: str = "Above",
) -> pd.DataFrame:
    """
    Compute probability that QoI exceeds or falls below a threshold.
    """
    qoi = samples[qoi_column]

    if direction == "Above":
        mask = qoi > threshold
        event = f"{qoi_column} > {threshold}"
    elif direction == "Below":
        mask = qoi < threshold
        event = f"{qoi_column} < {threshold}"
    else:
        raise ValueError("direction must be 'Above' or 'Below'.")

    probability = mask.mean()

    return pd.DataFrame([{
        "event": event,
        "threshold": threshold,
        "direction": direction,
        "probability": probability,
        "percent": 100 * probability,
        "n_samples": len(qoi),
    }])


def summarize_multiple_runs(runs, qoi_column: str = "QoI") -> pd.DataFrame:
    """
    Summarize QoI uncertainty across multiple runs/scenarios.
    """
    rows = []

    for run in runs:
        qoi = run.samples[qoi_column]

        rows.append({
            "scenario": run.label,
            "method": run.method,
            "mean": qoi.mean(),
            "std": qoi.std(),
            "median": qoi.median(),
            "q025": qoi.quantile(0.025),
            "q25": qoi.quantile(0.25),
            "q75": qoi.quantile(0.75),
            "q975": qoi.quantile(0.975),
            "min": qoi.min(),
            "max": qoi.max(),
        })

    return pd.DataFrame(rows)
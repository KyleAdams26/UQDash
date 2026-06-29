"""
Run objects used by UQdash.

An AnalysisRun stores the output of one completed sensitivity analysis.
It is intentionally method-agnostic, so it can represent Sobol, Morris,
FAST, or future methods.
"""

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class AnalysisRun:
    label: str
    method: str
    results: pd.DataFrame
    samples: pd.DataFrame
    parameter_names: list[str]
    parameter_info: dict[str, Any]
    model_path: str
    n_samples: int
    estimated_runs: int
    frozen_parameters: list[str]
    seed: int

    def main_metric(self) -> str:
        """
        Return the primary ranking metric for this analysis method.
        """
        if self.method == "Sobol":
            return "ST"

        if self.method == "Morris":
            return "mu_star"

        raise ValueError(f"Unsupported sensitivity method: {self.method}")

    def supports_total_order_comparison(self) -> bool:
        """
        Return whether this run has total-order sensitivity indices.

        Sobol and eFAST produce ST values. Morris does not.
        """
        return "ST" in self.results.columns

    def top_parameters(self, n: int | None = None) -> list[str]:
        """
        Return parameters sorted by the method's primary sensitivity metric.
        """
        metric = self.main_metric()

        ranked = (
            self.results
            .sort_values(metric, ascending=False)["parameter"]
            .tolist()
        )

        if n is None:
            return ranked

        return ranked[:n]

    def metadata(self) -> dict[str, Any]:
        """
        Return run metadata for JSON export.
        """
        return {
            "label": self.label,
            "method": self.method,
            "model_path": self.model_path,
            "n_samples": self.n_samples,
            "estimated_runs": self.estimated_runs,
            "frozen_parameters": self.frozen_parameters,
            "seed": self.seed,
            "parameter_info": self.parameter_info,
        }

    def results_csv(self) -> str:
        """
        Export the sensitivity-analysis results table as CSV.
        """
        return self.results.to_csv(index=False)

    def samples_csv(self) -> str:
        """
        Export the sampled parameter sets and QoI values as CSV.
        """
        return self.samples.to_csv(index=False)
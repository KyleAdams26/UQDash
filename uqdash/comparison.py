"""
Backend comparison utilities.

This module contains non-Streamlit logic for running multiple analysis
scenarios. The dashboard can call these functions, but they should not
contain UI code.
"""

from uqdash.analysis import run_sensitivity_analysis
from uqdash.run import AnalysisRun


def run_comparison(
    model_module,
    model_path: str,
    scenarios: list[dict],
    n_samples: int,
    seed: int,
    method: str = "Sobol",
) -> list[AnalysisRun]:
    """
    Run multiple Sobol analysis scenarios.

    Each scenario specifies which parameters are frozen. Parameters not
    frozen are sampled and varied.
    """
    parameter_names = list(model_module.PARAMETERS.keys())
    comparison_runs = []

    for scenario in scenarios:
        label = scenario["label"]
        frozen_parameters = scenario["frozen_parameters"]

        # Validate that all frozen parameters exist in the model.
        invalid = [
            param for param in frozen_parameters
            if param not in parameter_names
        ]

        if invalid:
            raise ValueError(
                f"Scenario '{label}' contains invalid parameters: {invalid}"
            )

        num_varying = len(parameter_names) - len(frozen_parameters)

        if num_varying == 0:
            raise ValueError(
                f"Scenario '{label}' freezes every parameter. "
                "At least one parameter must vary."
            )

        estimated_runs = n_samples * (num_varying + 2)

        # Run Sensitivity analysis for this frozen-parameter scenario.
        results, samples = run_sensitivity_analysis(
            method=method,
            model_module=model_module,
            n_samples=n_samples,
            frozen_parameters=frozen_parameters,
            seed=seed,
        )

        comparison_runs.append(
            AnalysisRun(
                method=method,
                label=label,
                results=results,
                samples=samples,
                parameter_names=parameter_names,
                parameter_info=model_module.PARAMETERS,
                model_path=model_path,
                n_samples=n_samples,
                estimated_runs=estimated_runs,
                frozen_parameters=frozen_parameters,
                seed=seed,
            )
        )

    return comparison_runs
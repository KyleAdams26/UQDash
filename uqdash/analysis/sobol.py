"""
Sobol sensitivity analysis.
"""

import pandas as pd

from SALib.sample import sobol as sobol_sample
from SALib.analyze import sobol as sobol_analyze

from uqdash.analysis.common import build_problem, evaluate_samples


def run_sobol(
    model_module,
    n_samples: int = 512,
    frozen_parameters: list[str] | None = None,
    seed: int = 1,
):
    """Run Sobol sensitivity analysis."""
    problem, varying_parameter_names = build_problem(
        model_module,
        frozen_parameters=frozen_parameters,
    )

    sampled_values = sobol_sample.sample(
        problem,
        n_samples,
        calc_second_order=False,
        seed=seed,
    )

    y, samples = evaluate_samples(
        model_module,
        sampled_values,
        varying_parameter_names,
    )

    indices = sobol_analyze.analyze(
        problem,
        y,
        calc_second_order=False,
    )

    results = pd.DataFrame({
        "parameter": varying_parameter_names,
        "S1": indices["S1"],
        "S1_conf": indices["S1_conf"],
        "ST": indices["ST"],
        "ST_conf": indices["ST_conf"],
    })

    return results, samples
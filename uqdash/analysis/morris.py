"""
Morris elementary-effects sensitivity analysis.
"""

import pandas as pd

from SALib.sample import morris as morris_sample
from SALib.analyze import morris as morris_analyze

from uqdash.analysis.common import build_problem, evaluate_samples


def run_morris(
    model_module,
    n_samples: int = 512,
    frozen_parameters: list[str] | None = None,
    seed: int = 1,
    num_levels: int = 4,
):
    """Run Morris elementary-effects sensitivity analysis."""
    problem, varying_parameter_names = build_problem(
        model_module,
        frozen_parameters=frozen_parameters,
    )

    sampled_values = morris_sample.sample(
        problem,
        N=n_samples,
        num_levels=num_levels,
        seed=seed,
    )

    y, samples = evaluate_samples(
        model_module,
        sampled_values,
        varying_parameter_names,
    )

    indices = morris_analyze.analyze(
        problem,
        sampled_values,
        y,
        num_levels=num_levels,
        seed=seed,
    )

    results = pd.DataFrame({
        "parameter": varying_parameter_names,
        "mu": indices["mu"],
        "mu_star": indices["mu_star"],
        "sigma": indices["sigma"],
        "mu_star_conf": indices["mu_star_conf"],
    })

    return results, samples
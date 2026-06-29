"""
Extended FAST sensitivity analysis.
"""

import pandas as pd

from SALib.sample import fast_sampler
from SALib.analyze import fast as fast_analyze

from uqdash.analysis.common import build_problem, evaluate_samples


def run_efast(
    model_module,
    n_samples: int = 512,
    frozen_parameters: list[str] | None = None,
    seed: int = 1,
    M: int = 4,
):
    """
    Run extended FAST sensitivity analysis.

    eFAST returns first-order indices S1 and total-order indices ST.
    """
    problem, varying_parameter_names = build_problem(
        model_module,
        frozen_parameters=frozen_parameters,
    )

    sampled_values = fast_sampler.sample(
        problem,
        N=n_samples,
        M=M,
        seed=seed,
    )

    y, samples = evaluate_samples(
        model_module,
        sampled_values,
        varying_parameter_names,
    )

    indices = fast_analyze.analyze(
        problem,
        y,
        M=M,
        seed=seed,
    )

    results = pd.DataFrame({
        "parameter": varying_parameter_names,
        "S1": indices["S1"],
        "ST": indices["ST"],
    })

    return results, samples
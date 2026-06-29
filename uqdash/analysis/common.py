"""
Common utilities for sensitivity-analysis methods.
"""

import numpy as np
import pandas as pd


def get_nominal_params(model_module) -> dict[str, float]:
    """Return nominal parameter values, using midpoint if nominal is absent."""
    nominal_params = {}

    for name, info in model_module.PARAMETERS.items():
        if "nominal" in info:
            nominal_params[name] = info["nominal"]
        else:
            low, high = info["bounds"]
            nominal_params[name] = 0.5 * (low + high)

    return nominal_params


def build_problem(model_module, frozen_parameters=None):
    """Build a SALib problem dictionary using only non-frozen parameters."""
    frozen_parameters = frozen_parameters or []

    all_parameter_names = list(model_module.PARAMETERS.keys())

    varying_parameter_names = [
        name for name in all_parameter_names
        if name not in frozen_parameters
    ]

    if not varying_parameter_names:
        raise ValueError("At least one parameter must vary.")

    bounds = [
        model_module.PARAMETERS[name]["bounds"]
        for name in varying_parameter_names
    ]

    problem = {
        "num_vars": len(varying_parameter_names),
        "names": varying_parameter_names,
        "bounds": bounds,
    }

    return problem, varying_parameter_names


def evaluate_samples(model_module, sampled_values, varying_parameter_names):
    """Evaluate model on sampled parameter values."""
    nominal_params = get_nominal_params(model_module)

    y = np.zeros(sampled_values.shape[0])
    full_samples = []

    for i, row in enumerate(sampled_values):
        params = nominal_params.copy()

        for name, value in zip(varying_parameter_names, row):
            params[name] = value

        y[i] = model_module.evaluate(params)
        full_samples.append(params.copy())

    samples = pd.DataFrame(full_samples)
    samples["QoI"] = y

    return y, samples
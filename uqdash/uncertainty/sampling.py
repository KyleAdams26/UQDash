"""
Independent sampling utilities for uncertainty propagation and parameter analysis.
"""

import numpy as np
import pandas as pd
from scipy.stats import qmc


def generate_uncertainty_samples(
    model_module,
    n_samples: int,
    seed: int = 1,
    sampler: str = "Sobol QMC",
    distribution: str = "Uniform",
):
    """
    Generate parameter samples.

    Parameters are sampled from their model-defined bounds. By default,
    samples are uniform over each parameter's interval.

    Supported distributions:
    - Uniform
    - Normal
    - Lognormal
    - Triangular
    """
    parameter_names = list(model_module.PARAMETERS.keys())

    bounds = np.array([
        model_module.PARAMETERS[name]["bounds"]
        for name in parameter_names
    ])

    lower_bounds = bounds[:, 0]
    upper_bounds = bounds[:, 1]
    n_parameters = len(parameter_names)

    unit_samples = generate_unit_samples(
        n_samples=n_samples,
        n_parameters=n_parameters,
        sampler=sampler,
        seed=seed,
    )

    sampled_values = transform_unit_samples(
        unit_samples=unit_samples,
        lower_bounds=lower_bounds,
        upper_bounds=upper_bounds,
        distribution=distribution,
    )

    return pd.DataFrame(
        sampled_values,
        columns=parameter_names,
    )


def generate_unit_samples(
    n_samples: int,
    n_parameters: int,
    sampler: str,
    seed: int,
):
    """
    Generate samples on the unit hypercube [0, 1]^d.
    """
    if sampler == "Random Monte Carlo":
        rng = np.random.default_rng(seed)
        return rng.random((n_samples, n_parameters))

    if sampler == "Sobol QMC":
        engine = qmc.Sobol(
            d=n_parameters,
            scramble=True,
            seed=seed,
        )
        return engine.random(n_samples)

    if sampler == "Latin Hypercube":
        engine = qmc.LatinHypercube(
            d=n_parameters,
            seed=seed,
        )
        return engine.random(n_samples)

    raise ValueError(f"Unsupported sampler: {sampler}")


def transform_unit_samples(
    unit_samples,
    lower_bounds,
    upper_bounds,
    distribution: str,
):
    """
    Transform unit samples into parameter samples.

    Uniform uses direct scaling.
    The other options are simple bounded distributions designed for dashboard
    exploration, not formal Bayesian prior modeling.
    """
    if distribution == "Uniform":
        return qmc.scale(
            unit_samples,
            lower_bounds,
            upper_bounds,
        )

    if distribution == "Triangular":
        return triangular_from_unit_samples(
            unit_samples,
            lower_bounds,
            upper_bounds,
        )

    if distribution == "Normal":
        return normal_from_unit_samples(
            unit_samples,
            lower_bounds,
            upper_bounds,
        )

    if distribution == "Lognormal":
        return lognormal_from_unit_samples(
            unit_samples,
            lower_bounds,
            upper_bounds,
        )

    raise ValueError(f"Unsupported parameter distribution: {distribution}")


def triangular_from_unit_samples(unit_samples, lower_bounds, upper_bounds):
    """
    Generate triangular samples with mode at the midpoint of each bound.
    """
    midpoint = 0.5 * (lower_bounds + upper_bounds)

    samples = np.empty_like(unit_samples)

    for j in range(unit_samples.shape[1]):
        lo = lower_bounds[j]
        hi = upper_bounds[j]
        mode = midpoint[j]

        c = (mode - lo) / (hi - lo)
        u = unit_samples[:, j]

        left = u < c

        samples[left, j] = lo + np.sqrt(u[left] * (hi - lo) * (mode - lo))
        samples[~left, j] = hi - np.sqrt(
            (1 - u[~left]) * (hi - lo) * (hi - mode)
        )

    return samples


def normal_from_unit_samples(unit_samples, lower_bounds, upper_bounds):
    """
    Generate approximately normal samples centered in the parameter bounds.

    Values are clipped to remain inside the parameter bounds.
    """
    from scipy.stats import norm

    clipped_unit_samples = np.clip(unit_samples, 1e-12, 1 - 1e-12)

    means = 0.5 * (lower_bounds + upper_bounds)
    stds = (upper_bounds - lower_bounds) / 4

    samples = norm.ppf(clipped_unit_samples, loc=means, scale=stds)

    return np.clip(samples, lower_bounds, upper_bounds)


def lognormal_from_unit_samples(unit_samples, lower_bounds, upper_bounds):
    """
    Generate bounded lognormal-like samples.

    This is useful for positive parameters where multiplicative uncertainty
    is more natural than additive uncertainty.
    """
    from scipy.stats import norm

    clipped_unit_samples = np.clip(unit_samples, 1e-12, 1 - 1e-12)

    safe_lower = np.maximum(lower_bounds, 1e-12)
    safe_upper = np.maximum(upper_bounds, safe_lower * 1.0001)

    log_lower = np.log(safe_lower)
    log_upper = np.log(safe_upper)

    log_means = 0.5 * (log_lower + log_upper)
    log_stds = (log_upper - log_lower) / 4

    log_samples = norm.ppf(
        clipped_unit_samples,
        loc=log_means,
        scale=log_stds,
    )

    samples = np.exp(log_samples)

    return np.clip(samples, lower_bounds, upper_bounds)


def evaluate_uncertainty_samples(model_module, parameter_samples):
    """
    Evaluate the model on sampled parameter sets.
    """
    qoi_values = []

    for _, row in parameter_samples.iterrows():
        params = row.to_dict()
        qoi_values.append(model_module.evaluate(params))

    results = parameter_samples.copy()
    results["QoI"] = qoi_values

    return results

def generate_selected_parameter_samples(
    model_module,
    varying_parameters,
    n_samples: int,
    seed: int = 1,
    sampler: str = "Sobol QMC",
):
    """
    Generate samples where only selected parameters vary.

    All non-selected parameters are fixed at their nominal/default values.
    """
    import numpy as np
    import pandas as pd
    from scipy.stats import qmc

    parameter_names = list(model_module.PARAMETERS.keys())

    base_values = {}

    for name, info in model_module.PARAMETERS.items():
        if "value" in info:
            base_values[name] = info["value"]
        elif "nominal" in info:
            base_values[name] = info["nominal"]
        else:
            raise KeyError(
                f"Parameter '{name}' must define either 'value' or 'nominal'."
            )

    varying_parameters = list(varying_parameters)

    if not varying_parameters:
        raise ValueError("Choose at least one parameter to vary.")

    bounds = np.array([
        model_module.PARAMETERS[name]["bounds"]
        for name in varying_parameters
    ])

    lower_bounds = bounds[:, 0]
    upper_bounds = bounds[:, 1]
    n_parameters = len(varying_parameters)

    if sampler == "Random Monte Carlo":
        rng = np.random.default_rng(seed)
        unit_samples = rng.random((n_samples, n_parameters))

    elif sampler == "Sobol QMC":
        engine = qmc.Sobol(
            d=n_parameters,
            scramble=True,
            seed=seed,
        )
        unit_samples = engine.random(n_samples)

    elif sampler == "Latin Hypercube":
        engine = qmc.LatinHypercube(
            d=n_parameters,
            seed=seed,
        )
        unit_samples = engine.random(n_samples)

    else:
        raise ValueError(f"Unsupported sampler: {sampler}")

    scaled_samples = qmc.scale(
        unit_samples,
        lower_bounds,
        upper_bounds,
    )

    rows = []

    for sample_row in scaled_samples:
        row = base_values.copy()

        for parameter, value in zip(varying_parameters, sample_row):
            row[parameter] = value

        rows.append(row)

    return pd.DataFrame(rows, columns=parameter_names)
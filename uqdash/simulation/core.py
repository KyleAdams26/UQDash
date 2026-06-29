"""
Core simulation utilities.
"""

import numpy as np
import pandas as pd


def get_nominal_params(model_module) -> dict:
    """
    Build a full parameter dictionary from nominal/default model values.
    """
    params = {}

    for name, info in model_module.PARAMETERS.items():
        if "value" in info:
            params[name] = info["value"]
        elif "nominal" in info:
            params[name] = info["nominal"]
        else:
            raise KeyError(
                f"Parameter '{name}' must define either 'value' or 'nominal'."
            )

    return params


def run_model_simulation(
    model_module,
    params: dict,
    t_final: float,
    n_time_points: int,
    method: str,
):
    """
    Run a model simulation.
    """
    if not hasattr(model_module, "simulate"):
        raise ValueError(
            "Model Simulation requires your model file to define "
            "`simulate(params, t_span, t_eval)`."
        )

    t_span = (0.0, float(t_final))
    t_eval = np.linspace(0.0, float(t_final), int(n_time_points))

    try:
        simulation_df = model_module.simulate(
            params=params,
            t_span=t_span,
            t_eval=t_eval,
            method=method,
        )
    except TypeError:
        simulation_df = model_module.simulate(
            params=params,
            t_span=t_span,
            t_eval=t_eval,
        )

    if not isinstance(simulation_df, pd.DataFrame):
        raise TypeError(
            "simulate(...) must return a pandas DataFrame with a `time` column."
        )

    if "time" not in simulation_df.columns:
        raise ValueError(
            "simulate(...) must return a DataFrame containing a `time` column."
        )

    return simulation_df
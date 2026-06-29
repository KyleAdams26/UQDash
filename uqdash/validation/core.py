"""
Core validation utilities.

Validation checks how well model predictions agree with observed data.
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


def compute_validation_predictions(model_module, data: pd.DataFrame, params: dict):
    """
    Compute model predictions for validation.

    Preferred model API:
        validation_predictions(params, data)

    Fallback model API:
        calibration_residuals(params, data)

    If calibration_residuals is used, UQDash reconstructs predictions as:
        prediction = observed + residual
    """
    if hasattr(model_module, "validation_predictions"):
        predictions = model_module.validation_predictions(params, data)
        return np.asarray(predictions, dtype=float)

    if hasattr(model_module, "calibration_residuals"):
        residuals = np.asarray(
            model_module.calibration_residuals(params, data),
            dtype=float,
        )

        observed = get_observed_values(data)

        return observed + residuals

    raise ValueError(
        "The model must define either validation_predictions(params, data) "
        "or calibration_residuals(params, data)."
    )


def get_observed_values(data: pd.DataFrame):
    """
    Extract observed values from a validation dataset.
    """
    if "observed" in data.columns:
        return data["observed"].to_numpy(dtype=float)

    if "observed_qoi" in data.columns:
        return data["observed_qoi"].to_numpy(dtype=float)

    if "observed_population" in data.columns:
        return data["observed_population"].to_numpy(dtype=float)

    raise ValueError(
        "Validation data must contain one of: "
        "'observed', 'observed_qoi', or 'observed_population'."
    )


def run_validation(model_module, data: pd.DataFrame, params: dict):
    """
    Validate model predictions against observed data.
    """
    observed = get_observed_values(data)
    predicted = compute_validation_predictions(
        model_module=model_module,
        data=data,
        params=params,
    )

    residuals = predicted - observed

    validation_df = data.copy()
    validation_df["observed"] = observed
    validation_df["predicted"] = predicted
    validation_df["residual"] = residuals
    validation_df["absolute_error"] = np.abs(residuals)
    validation_df["squared_error"] = residuals ** 2

    summary_df = compute_validation_metrics(observed, predicted)

    return {
        "summary": summary_df,
        "validation_data": validation_df,
        "params": params,
    }


def compute_validation_metrics(observed, predicted):
    """
    Compute common validation metrics.
    """
    residuals = predicted - observed

    sse = float(np.sum(residuals ** 2))
    mse = float(np.mean(residuals ** 2))
    rmse = float(np.sqrt(mse))
    mae = float(np.mean(np.abs(residuals)))

    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((observed - np.mean(observed)) ** 2))

    if ss_tot > 0:
        r_squared = 1 - ss_res / ss_tot
    else:
        r_squared = np.nan

    return pd.DataFrame([{
        "n_observations": len(observed),
        "SSE": sse,
        "MSE": mse,
        "RMSE": rmse,
        "MAE": mae,
        "R_squared": r_squared,
    }])
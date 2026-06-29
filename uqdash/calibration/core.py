"""
Core calibration utilities.

Calibration means estimating parameters by fitting model predictions
to observed data.

Multi-output calibration is supported using CSV columns named:

    time, observed_<state_name>

Example:
    time, observed_M2, observed_CAF, observed_TNBC
"""

import numpy as np
import pandas as pd
from scipy.optimize import least_squares, differential_evolution


def get_nominal_value(parameter_info: dict):
    """
    Get a parameter's nominal/default value.
    """
    if "value" in parameter_info:
        return parameter_info["value"]

    if "nominal" in parameter_info:
        return parameter_info["nominal"]

    raise KeyError("Each parameter must define either 'value' or 'nominal'.")


def get_parameter_bounds(model_module, parameters_to_estimate):
    """
    Get lower and upper bounds for estimated parameters.
    """
    lower_bounds = []
    upper_bounds = []

    for parameter in parameters_to_estimate:
        bounds = model_module.PARAMETERS[parameter]["bounds"]
        lower_bounds.append(bounds[0])
        upper_bounds.append(bounds[1])

    return np.array(lower_bounds), np.array(upper_bounds)


def vector_to_params(model_module, parameters_to_estimate, values):
    """
    Convert optimizer vector into a full parameter dictionary.
    """
    params = {
        name: get_nominal_value(info)
        for name, info in model_module.PARAMETERS.items()
    }

    for parameter, value in zip(parameters_to_estimate, values):
        params[parameter] = value

    return params


def detect_observed_variables(data: pd.DataFrame):
    """
    Detect observed variables from columns named observed_<variable>.
    """
    observed_variables = []

    for column in data.columns:
        if column.startswith("observed_"):
            observed_variables.append(column.replace("observed_", "", 1))

    return observed_variables


def simulate_for_observed_times(model_module, params, data):
    """
    Simulate model at the observed time points.
    """
    if "time" not in data.columns:
        raise ValueError("Calibration data must contain a 'time' column.")

    if not hasattr(model_module, "simulate"):
        raise ValueError(
            "Multi-output calibration requires model.simulate(params, t_span, t_eval)."
        )

    times = data["time"].to_numpy(dtype=float)

    return model_module.simulate(
        params=params,
        t_span=(float(times.min()), float(times.max())),
        t_eval=times,
    )


def compute_unweighted_fit_table(
    model_module,
    params,
    data: pd.DataFrame,
    selected_variables,
):
    """
    Build long-format table of observed, predicted, and residual values.
    """
    simulation_df = simulate_for_observed_times(
        model_module=model_module,
        params=params,
        data=data,
    )

    rows = []

    for variable in selected_variables:
        observed_column = f"observed_{variable}"

        if observed_column not in data.columns:
            raise ValueError(f"Missing column '{observed_column}' in calibration data.")

        if variable not in simulation_df.columns:
            raise ValueError(
                f"Model simulation output does not contain state '{variable}'."
            )

        observed = data[observed_column].to_numpy(dtype=float)
        predicted = simulation_df[variable].to_numpy(dtype=float)
        residual = predicted - observed

        for time, obs, pred, res in zip(data["time"], observed, predicted, residual):
            rows.append({
                "time": time,
                "variable": variable,
                "observed": obs,
                "predicted": pred,
                "residual": res,
            })

    return pd.DataFrame(rows)


def compute_residuals(
    model_module,
    data,
    parameters_to_estimate,
    values,
    selected_variables,
    variable_weights,
):
    """
    Compute weighted residual vector for optimization.
    """
    params = vector_to_params(
        model_module=model_module,
        parameters_to_estimate=parameters_to_estimate,
        values=values,
    )

    fit_df = compute_unweighted_fit_table(
        model_module=model_module,
        params=params,
        data=data,
        selected_variables=selected_variables,
    )

    weighted_residuals = []

    for variable in selected_variables:
        variable_residuals = fit_df.loc[
            fit_df["variable"] == variable,
            "residual",
        ].to_numpy(dtype=float)

        weight = float(variable_weights.get(variable, 1.0))
        weighted_residuals.extend(weight * variable_residuals)

    return np.asarray(weighted_residuals, dtype=float)


def run_least_squares_calibration(
    model_module,
    data: pd.DataFrame,
    parameters_to_estimate,
    selected_variables,
    variable_weights,
):
    """
    Estimate parameters using bounded nonlinear least squares.
    """
    lower_bounds, upper_bounds = get_parameter_bounds(
        model_module,
        parameters_to_estimate,
    )

    initial_guess = np.array([
        get_nominal_value(model_module.PARAMETERS[p])
        for p in parameters_to_estimate
    ])

    result = least_squares(
        fun=lambda values: compute_residuals(
            model_module=model_module,
            data=data,
            parameters_to_estimate=parameters_to_estimate,
            values=values,
            selected_variables=selected_variables,
            variable_weights=variable_weights,
        ),
        x0=initial_guess,
        bounds=(lower_bounds, upper_bounds),
    )

    return build_calibration_result(
        model_module=model_module,
        data=data,
        parameters_to_estimate=parameters_to_estimate,
        estimated_values=result.x,
        optimizer_result=result,
        method="Least Squares",
        selected_variables=selected_variables,
        variable_weights=variable_weights,
    )


def run_differential_evolution_calibration(
    model_module,
    data: pd.DataFrame,
    parameters_to_estimate,
    selected_variables,
    variable_weights,
    seed: int = 1,
):
    """
    Estimate parameters using differential evolution.
    """
    lower_bounds, upper_bounds = get_parameter_bounds(
        model_module,
        parameters_to_estimate,
    )

    bounds = list(zip(lower_bounds, upper_bounds))

    def objective(values):
        residuals = compute_residuals(
            model_module=model_module,
            data=data,
            parameters_to_estimate=parameters_to_estimate,
            values=values,
            selected_variables=selected_variables,
            variable_weights=variable_weights,
        )
        return float(np.sum(residuals ** 2))

    result = differential_evolution(
        func=objective,
        bounds=bounds,
        seed=seed,
        polish=True,
    )

    return build_calibration_result(
        model_module=model_module,
        data=data,
        parameters_to_estimate=parameters_to_estimate,
        estimated_values=result.x,
        optimizer_result=result,
        method="Differential Evolution",
        selected_variables=selected_variables,
        variable_weights=variable_weights,
    )


def build_calibration_result(
    model_module,
    data,
    parameters_to_estimate,
    estimated_values,
    optimizer_result,
    method,
    selected_variables,
    variable_weights,
):
    """
    Package fitted parameters, fit table, and diagnostics.
    """
    calibrated_params = vector_to_params(
        model_module=model_module,
        parameters_to_estimate=parameters_to_estimate,
        values=estimated_values,
    )

    fit_df = compute_unweighted_fit_table(
        model_module=model_module,
        params=calibrated_params,
        data=data,
        selected_variables=selected_variables,
    )

    fitted_parameters = pd.DataFrame({
        "parameter": parameters_to_estimate,
        "estimated_value": estimated_values,
        "nominal_value": [
            get_nominal_value(model_module.PARAMETERS[p])
            for p in parameters_to_estimate
        ],
    })

    overall_summary = summarize_fit(
        fit_df=fit_df,
        method=method,
        parameters_to_estimate=parameters_to_estimate,
        optimizer_result=optimizer_result,
    )

    variable_summary = summarize_fit_by_variable(fit_df)

    return {
        "method": method,
        "calibrated_params": calibrated_params,
        "fitted_parameters": fitted_parameters,
        "residuals": fit_df,
        "fit_table": fit_df,
        "summary": overall_summary,
        "variable_summary": variable_summary,
        "selected_variables": list(selected_variables),
        "variable_weights": dict(variable_weights),
        "optimizer_result": optimizer_result,
    }


def summarize_fit(fit_df, method, parameters_to_estimate, optimizer_result):
    """
    Compute overall calibration metrics.
    """
    residuals = fit_df["residual"].to_numpy(dtype=float)

    sse = float(np.sum(residuals ** 2))
    rmse = float(np.sqrt(np.mean(residuals ** 2)))
    mae = float(np.mean(np.abs(residuals)))

    return pd.DataFrame([{
        "method": method,
        "n_estimated_parameters": len(parameters_to_estimate),
        "n_fit_points": len(fit_df),
        "SSE": sse,
        "RMSE": rmse,
        "MAE": mae,
        "success": bool(getattr(optimizer_result, "success", True)),
        "message": str(getattr(optimizer_result, "message", "")),
    }])


def summarize_fit_by_variable(fit_df):
    """
    Compute calibration metrics separately for each observed variable.
    """
    rows = []

    for variable, group in fit_df.groupby("variable"):
        residuals = group["residual"].to_numpy(dtype=float)
        observed = group["observed"].to_numpy(dtype=float)

        ss_res = float(np.sum(residuals ** 2))
        ss_tot = float(np.sum((observed - np.mean(observed)) ** 2))

        rows.append({
            "variable": variable,
            "n_points": len(group),
            "SSE": ss_res,
            "RMSE": float(np.sqrt(np.mean(residuals ** 2))),
            "MAE": float(np.mean(np.abs(residuals))),
            "R_squared": 1 - ss_res / ss_tot if ss_tot > 0 else np.nan,
        })

    return pd.DataFrame(rows)
# UQDash API Reference

# Overview

This document describes the public interfaces used throughout UQDash. These APIs are intended for model developers, contributors, and advanced users extending the software.

Unless otherwise stated, all functions described here are considered part of the supported public interface.

---

# Model API

A compatible model should expose the following objects.

---

## PARAMETERS

```python
PARAMETERS: dict
```

Dictionary containing model parameter definitions.

Each parameter should define

* `nominal`
* `bounds`

Example

```python
PARAMETERS = {
    "r": {
        "nominal": 0.5,
        "bounds": [0.1, 1.0],
    }
}
```

---

## INITIAL_CONDITIONS

```python
INITIAL_CONDITIONS: dict
```

Dictionary mapping state names to initial values.

Example

```python
INITIAL_CONDITIONS = {
    "Tumor": 1000,
    "Immune": 500,
}
```

---

## STATE_NAMES

```python
STATE_NAMES: list[str]
```

Names of the simulated state variables.

These names should match the output columns produced by `simulate()`.

---

## rhs()

```python
rhs(
    t: float,
    y: list[float],
    params: dict,
) -> list[float]
```

Computes the model derivatives.

Required for ODE-based models.

---

## simulate()

```python
simulate(
    params: dict,
    t_span: tuple[float, float],
    t_eval=None,
    method="RK45",
) -> pandas.DataFrame
```

Runs a simulation and returns a DataFrame.

Required output columns

```
time
state_1
state_2
...
```

---

## evaluate()

```python
evaluate(
    params: dict,
) -> float
```

Computes the scalar quantity of interest (QoI).

Used by

* Sensitivity Analysis
* Parameter Analysis
* Uncertainty Propagation

---

## calibration_residuals()

Optional.

```python
calibration_residuals(
    params: dict,
    data: pandas.DataFrame,
)
```

Allows custom calibration objectives.

If omitted, UQDash computes residuals automatically.

---

# Simulation API

## run_model_simulation()

```python
run_model_simulation(
    model_module,
    params,
    t_final,
    n_time_points,
    method,
)
```

Runs a simulation using the selected numerical solver.

Returns

```
pandas.DataFrame
```

---

## get_nominal_params()

```python
get_nominal_params(
    model_module,
)
```

Returns

```
dict
```

containing nominal parameter values.

---

# Sensitivity Analysis API

## run_sensitivity_analysis()

```python
run_sensitivity_analysis(
    method,
    model_module,
    n_samples,
    frozen_parameters=None,
    seed=1,
)
```

Dispatches to the selected sensitivity method.

Supported methods

```
Sobol
Morris
eFAST
```

Returns

```
(results, samples)
```

---

## run_sobol()

```python
run_sobol(
    model_module,
    n_samples,
    frozen_parameters=None,
    seed=1,
)
```

Returns

```
results
samples
```

---

## run_morris()

```python
run_morris(...)
```

Runs Morris elementary effects.

---

## run_efast()

```python
run_efast(...)
```

Runs Extended FAST.

---

# Parameter Analysis API

## generate_uncertainty_samples()

```python
generate_uncertainty_samples(
    model_module,
    n_samples,
    sampler,
    distribution,
    seed,
)
```

Generates parameter samples.

Supported samplers

* Sobol QMC
* Latin Hypercube
* Random Monte Carlo

Supported distributions

* Uniform
* Normal
* Lognormal
* Triangular
* Beta

---

## generate_selected_parameter_samples()

```python
generate_selected_parameter_samples(
    model_module,
    varying_parameters,
    n_samples,
    sampler,
    seed,
)
```

Generates parameter samples while holding non-selected parameters fixed.

Used for scenario comparison.

---

## evaluate_uncertainty_samples()

```python
evaluate_uncertainty_samples(
    model_module,
    parameter_samples,
)
```

Evaluates the QoI for every sampled parameter set.

Returns

```
DataFrame
```

containing

* sampled parameters
* QoI

---

# Calibration API

## run_calibration()

```python
run_calibration(
    model_module,
    calibration_data,
    parameters_to_fit,
    variables_to_fit,
    optimizer,
    weights,
)
```

Runs parameter estimation.

Returns

```
CalibrationResult
```

---

## CalibrationResult

Primary fields

```python
best_parameters
```

```python
metrics
```

```python
predictions
```

```python
residuals
```

---

# Validation API

## run_validation()

```python
run_validation(
    model_module,
    validation_data,
    parameter_values,
)
```

Runs validation without changing parameters.

Returns

```
ValidationResult
```

---

## ValidationResult

Primary fields

```python
predictions
```

```python
metrics
```

```python
residuals
```

---

# Report API

All report generators return the output directory.

---

## generate_sensitivity_report()

```python
generate_sensitivity_report(
    output_root,
    ...
)
```

---

## generate_parameter_analysis_report()

```python
generate_parameter_analysis_report(...)
```

---

## generate_uncertainty_report()

```python
generate_uncertainty_report(...)
```

---

## generate_calibration_report()

```python
generate_calibration_report(...)
```

---

## generate_validation_report()

```python
generate_validation_report(...)
```

---

# Plot API

Common plotting functions include

## Simulation

```python
plot_simulation_trajectories(...)
```

---

## Sensitivity

```python
plot_sensitivity_bar(...)
```

---

## Parameter Analysis

```python
plot_parameter_scatter(...)
```

```python
plot_projection_grid(...)
```

```python
plot_3d_projection(...)
```

```python
plot_3d_projection_static(...)
```

---

## Uncertainty

```python
plot_uncertainty_histogram(...)
```

```python
plot_prediction_intervals(...)
```

```python
plot_exceedance_probability(...)
```

---

## Calibration

```python
plot_calibration_results(...)
```

---

## Validation

```python
plot_validation_results(...)
```

---

# Dashboard API

Each dashboard tab provides a single entry point.

```python
display_home_tab(settings)
```

```python
display_simulation_tab(settings)
```

```python
display_sensitivity_tab(settings)
```

```python
display_parameter_tab(settings)
```

```python
display_uncertainty_tab(settings)
```

```python
display_calibration_tab(settings)
```

```python
display_validation_tab(settings)
```

Each function receives the global settings dictionary generated by the sidebar.

---

# Sidebar API

```python
display_sidebar()
```

Returns a dictionary containing

```
model_path

sample_power

n_samples

seed

plot_style
```

These settings are passed to each dashboard tab.

---

# Session State

Common session state variables include

```python
simulation_df
```

```python
sensitivity_run
```

```python
sobol_run
```

```python
parameter_analysis_samples
```

```python
uncertainty_samples
```

```python
calibration_result
```

```python
validation_result
```

These values enable communication between dashboard tabs during a session.

---

# Report Output

Reports are written to timestamped directories.

Typical structure

```text
reports/
    calibration/
        run_20260701_153455/

    sensitivity/
        run_20260701_154210/

    uncertainty/
        run_20260701_155600/
```

Each report may contain

* Markdown summary
* CSV tables
* JSON metadata
* Figures
* Analysis settings

---

# Extension Points

UQDash is designed to be extensible.

Common extensions/updates may include

* New sampling methods
* Additional sensitivity algorithms
* New data-fitting methods
* Additional uncertainty distributions
* New plotting utilities
* Custom report templates
* Additional dashboard tabs


---

# Error Handling

Public API functions should

* validate inputs,
* raise informative exceptions,
* preserve reproducibility,
* and avoid silently modifying user data.

Errors are reported through the dashboard interface while preserving detailed Python tracebacks for debugging.

---

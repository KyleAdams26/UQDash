# UQDash User Guide

## Introduction

Welcome to **UQDash**, an interactive dashboard for uncertainty quantification, sensitivity analysis, parameter exploration, calibration, and validation of mathematical and computational models.

UQDash is designed to provide an end-to-end workflow for understanding model behavior. Rather than writing analysis scripts manually, users can load a compatible model file and perform common uncertainty quantification tasks through an intuitive graphical interface.

---

# Getting Started

Launch the dashboard from the project directory:

```bash
streamlit run app.py
```

The dashboard opens in your default web browser.

The left sidebar contains global settings that apply throughout the application. These mostly include color options for plots.

---

# Sidebar Settings

## Model File

Specify the Python model to analyze.

Example:

```
examples/logistic_model.py
```

or

```
examples/tnbc_model.py
```

---

## Sampling Settings

These settings control analyses that require parameter sampling.

### Base Sample Size

Specified as

[
2^k
]

For example

| Power | Samples |
| ----: | ------: |
|     8 |     256 |
|     9 |     512 |
|    10 |    1024 |
|    11 |    2048 |

Larger sample sizes generally improve accuracy but require additional model evaluations.

---

## Random Seed

Controls reproducibility of randomized analyses.

Using the same seed with identical settings should produce identical results.

---

## Plot Theme

Choose from several built-in themes or create a custom theme.

Custom themes allow control over

* primary colors
* secondary colors
* bar orientation
* transparency
* projection colormaps

These settings automatically apply across supported visualizations.

---

# Dashboard Overview

The dashboard is organized into several analysis tabs.

---

# Home

The landing page summarizes the purpose of UQDash and provides a recommended workflow.

Recommended order:

1. Simulate your model.
2. Perform sensitivity analysis.
3. Explore parameter interactions.
4. Propagate uncertainty.
5. Calibrate parameters.
6. Validate the calibrated model.
7. Export reports.

---

# Model Simulation

The Simulation tab integrates the model over time using SciPy ODE solvers.

## Controls

* Final simulation time
* Number of time points
* Solver method
* Parameter values

Supported solvers include

* RK45
* RK23
* DOP853
* Radau
* BDF
* LSODA

## Outputs

* Individual trajectory plots for each state variable
* Simulation data table

Simulation results are useful for verifying that the model behaves as expected before beginning uncertainty analyses.

---

# Sensitivity Analysis

The Sensitivity Analysis tab identifies influential model parameters.

Supported methods include

* Sobol
* Morris Elementary Effects
* Extended FAST (eFAST)

## Outputs

* Sensitivity index table
* Parameter rankings
* Bar plots
* Method comparison
* Convergence diagnostics

Sobol total-order indices are also used throughout UQDash to rank parameters in dropdown menus and calibration controls.

---

# Parameter Analysis

Parameter Analysis explores relationships between parameter values and the quantity of interest (QoI).

Unlike sensitivity analysis, this section focuses on visualization and interpretation rather than sensitivity indices.

## Features

### QoI Summary

Displays summary statistics and prediction intervals.

---

### Scenario Comparison

Compare

* all parameters varying

versus

* only selected parameters varying

while all remaining parameters remain fixed at nominal values.

This helps determine whether a small subset of influential parameters explains most of the output variability.

---

### Single-Parameter Scatter

Visualize the relationship between one parameter and the QoI.

---

### Projection Plots

Generate pairwise projections of selected parameters colored by QoI.

The QoI color scale can be manually adjusted to emphasize different regions of parameter space.

---

### 3D Projection

Explore parameter interactions using either

* static Matplotlib figures

or

* interactive Plotly visualizations.

---

# Uncertainty Propagation

Uncertainty propagation estimates the distribution of model outputs induced by uncertain parameter values.

Supported sampling methods

* Sobol Quasi-Monte Carlo
* Latin Hypercube Sampling
* Random Monte Carlo

Supported parameter distributions include

* Uniform
* Normal
* Lognormal

## Outputs

* QoI histogram
* Summary statistics
* Prediction intervals
* Threshold probabilities
* Scenario comparison

---

# Calibration

Calibration estimates model parameters from observed data.

## Required CSV Format

The input file must contain

* a `time` column (must be lowercase!)
* one or more observed state variables

Example

| time | observed_TNBC | observed_Tc |
| ---: | ------------: | ----------: |
|    0 |          2100 |       66800 |
|   20 |          2600 |       64000 |
|   40 |          3200 |       61500 |

Observed variable names must begin with

```
observed_
```

followed by the model state name.

For example

```
observed_TNBC
```

corresponds to the simulated state

```
TNBC
```

---

## Parameter Selection

Choose which parameters to estimate.

If a Sobol analysis has already been performed, parameters are automatically ordered from most to least influential.

---

## Variable Selection

Choose which observed variables should contribute to the objective function.

Multiple variables may be fitted simultaneously.

---

## Variable Weighting

Variable weights determine the relative contribution of each variable to the optimization objective.

Normalization by the maximum observed value is recommended when variables differ substantially in magnitude.

---

## Outputs

Calibration produces

* fitted parameter estimates
* goodness-of-fit metrics
* model-versus-data plots
* calibration report

---

# Validation

Validation evaluates calibrated or externally supplied parameters using an independent dataset.

Unlike calibration, parameter values remain fixed during validation.

Validation data should follow the same CSV format as calibration data.

Outputs include

* model predictions
* observed data
* residual statistics
* validation metrics
* validation report

---

# Report Generation

Most tabs support automatic report generation.

Reports include

* analysis settings
* metadata
* summary tables
* publication-quality figures

Reports are saved inside the selected output directory.

---

# Preparing Your Own Model

A compatible model should define

* `PARAMETERS`
* `simulate()`
* `evaluate()`

Optionally,

* `calibration_residuals()`

Refer to the Model Developer Guide for the complete API specification.

---

# Tips

* Begin with the Simulation tab to verify model behavior.
* Increase sample size for more accurate Sobol indices.
* Use Sobol analysis before calibration to identify influential parameters.
* Normalize variable weights during calibration when state variables differ greatly in magnitude.
* Validate calibrated parameters using an independent dataset whenever possible.
* Generate reports after each major analysis to preserve settings and results.

---

# Troubleshooting

## Calibration converges poorly

Possible causes include

* poor initial parameter guesses
* too many parameters estimated simultaneously
* inconsistent units
* poorly scaled residuals

---

## Sensitivity results vary substantially

Increase the base sample size.

---

## Simulation fails

Verify

* parameter bounds
* initial conditions
* model equations
* solver choice

---

# Additional Documentation

Additional guides are available for

* Model Development
* Calibration
* Validation
* API Reference

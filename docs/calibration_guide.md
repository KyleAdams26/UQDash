# UQDash Calibration Guide

# Introduction

Model calibration is the process of estimating unknown model parameters using observed data. In UQDash, calibration adjusts selected parameters so that simulated model outputs best match experimental or observational measurements.

Calibration is often performed after model development and before validation. A well-calibrated model provides parameter estimates that can be used for prediction, uncertainty quantification, and sensitivity analysis.

---

# Calibration Workflow

A typical calibration workflow in UQDash is

1. Prepare a compatible model.
2. Collect experimental or observational data.
3. Select parameters to estimate.
4. Choose observed variables to fit.
5. Select an optimization algorithm.
6. Run the calibration.
7. Evaluate goodness-of-fit.
8. Validate the fitted model using independent data.

---

# Calibration Data Format

Calibration data must be uploaded as a CSV file.

The first column must be

```text
time
```

Each observed variable should begin with

```text
observed_
```

followed by the model state name.

Example

| time | observed_TNBC | observed_Tc | observed_Treg |
| ---: | ------------: | ----------: | ------------: |
|    0 |          2090 |       66800 |         10900 |
|   20 |          2510 |       64000 |         11320 |
|   40 |          3195 |       61800 |         11810 |

The model output columns

```text
TNBC
Tc
Treg
```

must exactly match

```text
observed_TNBC
observed_Tc
observed_Treg
```

---

# Selecting Parameters

Only parameters selected by the user are estimated.

All remaining parameters remain fixed at their nominal values.

For large mechanistic models, estimating every parameter simultaneously is rarely recommended. Instead:

If a Sobol analysis has been run in UQDash, parameter lists are automatically ordered by descending total-order Sobol index.

---

# Selecting Variables

Calibration may use one or more observed variables.

Examples include

* Tumor population only
* Tumor and immune populations
* All measured state variables

Including additional variables generally provides more information but may also increase the complexity of the optimization problem.

---

# Variable Weighting

Different state variables often have very different magnitudes.

Example

| Variable | Typical Magnitude |
| -------- | ----------------: |
| CAF      |               700 |
| Tumor    |             2,000 |
| M2       |            20,000 |
| Tc       |           120,000 |

Without weighting, variables with larger values dominate the objective function.

UQDash supports several weighting strategies.

## Equal Weights

Every residual contributes equally.

Suitable when variables have similar scales.

---

## Normalize by Maximum

Residuals are divided by the maximum observed value for each variable.

This prevents large populations from dominating the optimization and is recommended for most biological models.

---

## Manual Weights

Users may specify custom weights for each observed variable.

This is useful when certain variables are considered more reliable or more biologically important.

---

# Optimization Methods

UQDash currently supports the following fitting methods.

## Nonlinear Least Squares

Equivalent to MATLAB's `lsqcurvefit`.

Advantages

* Fast
* Efficient for smooth ODE models
* Suitable for most calibration problems

Limitations

* Local optimization
* Sensitive to initial parameter values

---

## Differential Evolution

A population-based global optimization algorithm.

Advantages

* Does not require an initial guess
* Better at avoiding local minima
* Well suited for highly nonlinear models

Limitations

* Slower than least squares
* Requires more model evaluations

---

Additional methods may be added in the future.

# Objective Function

Calibration minimizes the discrepancy between model predictions and observed data.

By default, UQDash minimizes the sum of squared residuals:

[
\min_{\theta}
\sum_i
\left(
y_i-\hat y_i(\theta)
\right)^2
]

where

* (y_i) is an observed measurement
* (\hat y_i) is the corresponding model prediction
* (\theta) denotes the estimated parameter vector

Future releases may support additional objective functions such as maximum likelihood estimation.

---

# Running a Calibration

1. Open the **Calibration** tab.
2. Select a calibration data file.
3. Choose the parameters to estimate.
4. Select the observed variables to fit.
5. Specify variable weights if desired.
6. Choose an optimization method.
7. Click **Run Calibration**.

Progress indicators are displayed while the optimization is running.

---

# Calibration Outputs

Successful calibration produces

* Estimated parameter values
* Goodness-of-fit metrics
* Model-versus-data plots
* Residual statistics
* Calibration report

Model predictions are plotted alongside the observed data for each fitted variable, allowing visual assessment of the fit.

---

# Interpreting Results

A good calibration should produce

* Good agreement between model and data
* Biologically reasonable parameter estimates
* Stable optimization results

Poor calibration may indicate

* Inappropriate parameter bounds
* Incorrect model structure
* Insufficient data
* Parameter non-identifiability
* Inconsistent measurement units

---

# Best Practices

* Verify that the model simulates correctly before calibration.
* Begin by estimating only a small number of influential parameters.
* Use global sensitivity analysis to prioritize parameter selection.
* Normalize residuals when variables differ greatly in scale.
* Inspect fitted parameter values for biological plausibility.
* Validate calibrated parameters using independent datasets whenever possible.

---

# Common Calibration Challenges

## Poor Convergence

Possible causes include

* Poor initial parameter guesses
* Excessively wide parameter bounds
* Too many parameters estimated simultaneously
* Incorrect model equations

---

## Large Residuals

Possible causes include

* Measurement noise
* Incorrect units
* Missing biological mechanisms
* Inappropriate weighting

---

## Parameters at Bounds

If estimated parameters repeatedly converge to their lower or upper bounds, consider

* expanding the parameter range,
* revisiting the model assumptions,
* or determining whether the parameter is identifiable from the available data.

---

# Calibration Reports

UQDash automatically generates calibration reports containing

* Calibration settings
* Estimated parameters
* Goodness-of-fit statistics
* Diagnostic plots
* Metadata
* Timestamped output directory

These reports provide a permanent record of the calibration procedure and support reproducible research.

---

# Recommended Workflow

A typical UQDash analysis proceeds as follows:

1. Develop the mathematical model.
2. Verify model behavior using the **Simulation** tab.
3. Identify influential parameters using **Sensitivity Analysis**.
4. Explore parameter effects with **Parameter Analysis**.
5. Estimate unknown parameters using **Calibration**.
6. Assess predictive performance using **Validation**.
7. Quantify prediction uncertainty using **Uncertainty Propagation**.
8. Export reports for documentation and publication.

Following this workflow helps ensure that calibrated models are interpretable, reproducible, and suitable for downstream uncertainty and sensitivity analyses.

# UQDash Validation Guide

# Introduction

Model validation evaluates how well a calibrated model predicts data that were **not used during parameter estimation**. While calibration adjusts model parameters to fit observed measurements, validation assesses the model's predictive performance on independent datasets.

Validation is an essential step in model development because a model that fits calibration data well may still perform poorly when predicting new observations. UQDash provides a streamlined workflow for validating parameter sets and visualizing prediction accuracy.

---

# Calibration vs. Validation

Although calibration and validation use similar types of data, they serve different purposes.

| Calibration                          | Validation                           |
| ------------------------------------ | ------------------------------------ |
| Estimates unknown parameters         | Tests predictive performance         |
| Parameters are optimized             | Parameters remain fixed              |
| Uses calibration dataset             | Uses an independent dataset          |
| Improves agreement with observations | Evaluates generalization to new data |

Whenever possible, calibration and validation should use different datasets.

---

# Validation Workflow

A typical validation workflow in UQDash is

1. Develop the mathematical model.
2. Calibrate model parameters.
3. Collect an independent validation dataset.
4. Select the parameter values to validate.
5. Run the simulation.
6. Compare predictions with observations.
7. Evaluate goodness-of-fit.
8. Generate a validation report.

---

# Validation Data Format

Validation data must be uploaded as a CSV file using the same format as calibration data.

The first column must be

```text 
time
```

Observed variables should begin with

```text 
observed_
```

followed by the corresponding model state name.

Example

| time | observed_TNBC | observed_Tc | observed_Treg |
| ---: | ------------: | ----------: | ------------: |
|    0 |          2100 |       66900 |         10890 |
|   20 |          2490 |       64650 |         11380 |
|   40 |          3150 |       62100 |         11820 |

The state names following `observed_` must exactly match the simulation output column names.

---

# Choosing Parameters to Validate

UQDash offers two approaches for validation.

## Use Latest Calibrated Parameters

If a calibration has been performed during the current session, the most recently estimated parameter values can be used directly.

This is the recommended workflow when evaluating a newly calibrated model.

---

## Manually Specify Parameters

Users may also enter parameter values manually.

This option is useful when

* parameters were estimated using external software,
* literature values are available,
* multiple published parameter sets are being compared,
* or historical parameter estimates are being evaluated.

Each parameter entered manually overrides its nominal value for the validation simulation.

---

# Running a Validation

1. Open the **Validation** tab.
2. Load a validation CSV file.
3. Select the parameter source.
4. If necessary, enter parameter values manually.
5. Click **Run Validation**.

The model is simulated using the selected parameters, and predictions are compared directly with the validation dataset.

---

# Validation Outputs

Successful validation produces

* Model prediction plots
* Observed data overlays
* Variable-by-variable comparisons
* Residual statistics
* Goodness-of-fit metrics
* Validation report

Each observed variable is displayed in its own panel, making it easier to identify variables that are well predicted and those that may require further model refinement.

---

# Goodness-of-Fit Metrics

UQDash reports several common measures of predictive accuracy.

## Root Mean Squared Error (RMSE)

Measures the average prediction error.

Lower values indicate better agreement.

---

## Mean Absolute Error (MAE)

Measures the average absolute prediction error.

Unlike RMSE, MAE is less sensitive to large individual errors.

---

## Coefficient of Determination (R²)

Measures the proportion of variation explained by the model.

Values closer to one indicate stronger predictive performance.

---

## Residuals

Residuals are computed as

[
\text{Residual} =
\text{Prediction}
-----------------

\text{Observation}
]

Residual plots help identify

* systematic bias,
* incorrect model structure,
* missing biological mechanisms,
* or time-dependent errors.

---

# Interpreting Validation Results

A successful validation should demonstrate

* close agreement between predictions and observations,
* small residuals,
* consistent performance across variables,
* and biologically plausible trajectories.

Validation does **not** require a perfect fit. Small discrepancies are expected due to measurement noise, model simplifications, and biological variability.

---

# Common Validation Outcomes

## Excellent Validation

* Predictions closely follow observations.
* Residuals fluctuate randomly around zero.
* All variables are reproduced reasonably well.

This suggests that the calibrated model generalizes effectively.

---

## Moderate Validation

* Major trends are captured.
* Small systematic deviations exist.
* Some variables are reproduced more accurately than others.

Further refinement may improve predictive performance.

---

## Poor Validation

Common causes include

* overfitting during calibration,
* insufficient calibration data,
* incorrect parameter estimates,
* model structural errors,
* or differences between calibration and validation experiments.

Poor validation results often indicate that the model should be revised rather than simply recalibrated.

---

# Best Practices

* Always validate using data that were **not** used during calibration.
* Use the same units in both simulation and validation data.
* Compare multiple state variables whenever possible.
* Inspect plots visually in addition to numerical metrics.
* Evaluate whether fitted parameters remain biologically reasonable.
* Repeat validation when model equations or parameters change.

---

# Validation Reports

UQDash automatically generates validation reports containing

* Validation settings
* Parameter source
* Parameter values
* Goodness-of-fit statistics
* Variable comparison plots
* Metadata
* Timestamped output directory

These reports provide a reproducible record of model performance and can be included in project documentation or publications.

---

# Troubleshooting

## Model Predictions Do Not Match Observations

Check that

* the correct parameter set is being used,
* time units are consistent,
* observed variable names match simulation outputs,
* and validation data were collected under the same experimental conditions represented by the model.

---

## Validation Metrics Are Poor

Possible causes include

* calibration overfitting,
* inadequate calibration data,
* unrealistic parameter bounds,
* incorrect initial conditions,
* or missing biological mechanisms.

In many cases, revisiting the model formulation is more appropriate than further tuning parameters.

---

# Recommended Workflow

A typical UQDash modeling workflow is

1. Develop the mathematical model.
2. Verify model behavior using the **Simulation** tab.
3. Perform **Sensitivity Analysis** to identify influential parameters.
4. Explore parameter interactions with **Parameter Analysis**.
5. Estimate unknown parameters using **Calibration**.
6. Evaluate predictive performance using **Validation**.
7. Quantify prediction uncertainty with **Uncertainty Propagation**.
8. Export reports documenting each stage of the analysis.

Following this workflow promotes reproducible, interpretable, and scientifically robust model development.

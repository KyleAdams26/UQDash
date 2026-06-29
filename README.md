# UQDash

**UQDash** is an interactive dashboard for **uncertainty quantification (UQ)**, **global sensitivity analysis**, **parameter exploration**, **model calibration**, and **validation** of mathematical and computational models.

Built with **Python**, **Streamlit**, **SALib**, **SciPy**, and **Matplotlib**, UQDash provides a unified workflow for exploring model behavior without requiring users to write custom analysis scripts.

---

## Features

### Model Simulation

* Simulate arbitrary ODE models
* Adjustable solver methods
* Interactive parameter editing
* Individual trajectory plots for each state variable

---

### Global Sensitivity Analysis

Supported methods:

* Sobol
* Morris Elementary Effects
* Extended FAST (eFAST)

Outputs include

* Sensitivity index tables
* Ranked parameter importance
* Convergence diagnostics
* Method comparison
* Exportable reports

---

### Parameter Analysis

Explore how uncertain parameters influence model outputs.

Features include

* QoI distribution comparison
* Single-parameter scatter plots
* Pairwise projection plots
* Static and interactive 3D projections
* PCA/manifold exploration

---

### Uncertainty Propagation

Study uncertainty in model outputs induced by uncertain parameters.

Supported sampling methods

* Sobol Quasi-Monte Carlo
* Latin Hypercube Sampling
* Random Monte Carlo

Outputs include

* QoI histograms
* Summary statistics
* Prediction intervals
* Threshold probabilities
* Scenario uncertainty comparison
* Uncertainty metrics reports
---

### Calibration

Estimate model parameters from experimental  data.

Supported features

* Multiple optimization methods
* Multi-variable fitting
* Variable weighting
* Fit diagnostics
* Model vs. data visualization
* Exportable calibration reports

---

### Validation

Evaluate calibrated models on independent datasets.

Supported features

* Model vs. validation data
* Goodness-of-fit metrics
* Variable-by-variable comparison
* Validation reports

---

### Automatic Report Generation

Generate publication-ready reports for

* Sensitivity Analysis
* Parameter Analysis
* Uncertainty Propagation
* Calibration
* Validation

Reports include figures, summary tables, metadata, and analysis settings.

---
## Prerequisites

Before installing UQDash, ensure the following software is installed:

- Python 3.11 or newer (Python 3.13 is supported)
- pip (Python package manager)
- Git (optional, for cloning the repository)

You can verify your Python installation by running

```bash
python --version
```

## Installation

Clone the repository

```bash
git clone https://github.com/<KyleAdams26>/UQDash.git
cd UQDash
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment

Windows

```bash
.venv\Scripts\activate
```

macOS/Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the dashboard

```bash
streamlit run app.py
```

---

## Quick Start

1. Launch UQDash.

2. Load a model file.

The included example

```
examples/logistic_model.py
```

is a good starting point.

3. Run a model simulation.

4. Perform a sensitivity analysis.

5. Explore parameter interactions.

6. Propagate parameter uncertainty.

7. Calibrate model parameters using observed data.

8. Validate the calibrated model on independent data.

9. Export reports.

---

## Creating Your Own Model

Every model should define

```python
PARAMETERS
```

A dictionary containing

* nominal values
* parameter bounds

Example

```python
PARAMETERS = {
    "r": {
        "nominal": 0.5,
        "bounds": [0.1, 1.0],
    },
}
```

---

A simulation function

```python
simulate(params, t_span, t_eval, method="RK45")
```

which returns a pandas DataFrame

Example columns

```
time
Tumor
ImmuneCells
Cytokines
```

---

A quantity-of-interest function

```python
evaluate(params)
```

which returns a scalar QoI for sensitivity and uncertainty analyses.

---

Optional calibration helper

```python
calibration_residuals(params, data)
```

for custom calibration workflows.

---

## Project Structure

```
UQDash/
│
├── app.py
├── README.md
├── requirements.txt
│
├── examples/
│
└── uqdash/
    ├── analysis/
    ├── calibration/
    ├── dashboard/
    ├── diagnostics/
    ├── exploration/
    ├── plots/
    ├── reports/
    ├── simulation/
    ├── uncertainty/
    └── validation/
```

---

## Supported Sampling Methods

* Sobol Quasi-Monte Carlo
* Latin Hypercube Sampling
* Random Monte Carlo

---

## Supported Sensitivity Methods

* Sobol
* Morris
* Extended FAST (eFAST)

---

## Supported Calibration Methods

Current support includes

* Nonlinear Least Squares
* Differential Evolution

Additional optimization methods are planned.

---

## Dependencies

Major libraries include

* Streamlit
* NumPy
* SciPy
* Pandas
* Matplotlib
* Plotly
* SALib
* Others

---

## Citation

If you use UQDash in academic work, please cite ?.

---

## Acknowledgments

UQDash was developed by Kyle Adams to simplify uncertainty quantification, sensitivity analysis, calibration, and validation workflows for mechanistic mathematical models across scientific disciplines. Development of portions of this software was assisted by OpenAI's ChatGPT for code and comment generation, debugging, and documentation.

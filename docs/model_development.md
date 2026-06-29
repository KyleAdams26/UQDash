# UQDash Model Development Guide

## Overview

UQDash is designed to analyze user-defined mathematical models with minimal modification. Rather than requiring a specific modeling framework, UQDash expects each model file to have a set of standard variables and functions.

Any model satisfying this interface can be used for

* Model simulation
* Global sensitivity analysis
* Parameter analysis
* Uncertainty propagation
* Parameter calibration
* Model validation
* Automatic report generation

Although many examples use systems of ordinary differential equations (ODEs), UQDash is not restricted to ODE models. Any deterministic model capable of evaluating a quantity of interest can be adapted. (Only ODEs have been tested)

---

# Required Model Components

A compatible model file should contain the following components.

## 1. PARAMETERS

`PARAMETERS` defines the model parameters available to UQDash.

Each parameter should include

* a nominal value
* lower and upper bounds

Example

```python
PARAMETERS = {
    "growth_rate": {
        "nominal": 0.5,
        "bounds": [0.1, 1.0],
    },
    "carrying_capacity": {
        "nominal": 100.0,
        "bounds": [50.0, 200.0],
    },
}
```

or

```python
PARAMETERS = {
    "gR": {
        "nominal": 0.5,
        "bounds": [0.1, 1.0],
    },
    "K_R": {
        "nominal": 100.0,
        "bounds": [50.0, 200.0],
    },
}
```

These bounds are used by

* sensitivity analysis
* uncertainty propagation
* parameter analysis
* calibration

---

## 2. INITIAL_CONDITIONS

State variables should be initialized through a dictionary.

Example

```python
INITIAL_CONDITIONS = {
    "Tumor": 1000.0,
    "Immune": 500.0,
}
```

or 

```python
INITIAL_CONDITIONS = {
    "T": 1000.0,
    "I": 500.0,
}
```

These values are used by the simulation engine unless modified during calibration.

---

## 3. STATE_NAMES

Provide the names of all state variables.

Example

```python
STATE_NAMES = [
    "Tumor",
    "Immune",
]
```

or

```python
STATE_NAMES = [
    "T",
    "I",
]
```

These names are used throughout the dashboard when generating plots and matching calibration or validation data.

---

## 4. rhs()

ODE models should define a right-hand side function.

Example

```python
def rhs(t, y, params):
    """
    Compute the derivatives of the state variables.
    """
    tumor = y[0]
    immune = y[1]

    growth = params["growth_rate"]

    dTumor = growth * tumor
    dImmune = -0.05 * immune

    return [
        dTumor,
        dImmune,
    ]
```

Although the function name is not strictly required, using `rhs()` is recommended for consistency.

---

## 5. simulate()

The simulation function is required.


Example

```python
def simulate(params, t_span, t_eval, method="RK45"):
    """
    Simulate logistic growth and return a trajectory DataFrame.
    """
    import pandas as pd
    from scipy.integrate import solve_ivp

    r = params["r"]
    K = params["K"]
    x0 = params["x0"]

    sol = solve_ivp(
        lambda t, x: logistic_growth(t, x, r, K),
        t_span=t_span,
        y0=[x0],
        t_eval=t_eval,
        method=method,
    )

    return pd.DataFrame({
        "time": sol.t,
        "population": sol.y[0],
    })
```

The function should

* solve the model
* return a pandas DataFrame
* include a `time` column

Example return value

| time | Tumor | Immune |
| ---: | ----: | -----: |
|    0 |  1000 |    500 |
|    1 |  1030 |    492 |
|    2 |  1064 |    484 |

UQDash uses this function for

* Model Simulation
* Calibration
* Validation

---

## 6. evaluate()

Sensitivity analysis and uncertainty propagation require a scalar quantity of interest (QoI).

The model should define

```python
def evaluate(params):
```

This function accepts a parameter dictionary and returns a single scalar.

Example

```python
def evaluate(params):

    simulation = simulate(params)

    return simulation["Tumor"].iloc[-1]
```

Possible QoIs include

* final tumor size
* peak population
* cumulative drug dose
* area under the curve
* extinction time

The QoI should be selected to reflect the scientific question of interest.

---

# Optional Components

## calibration_residuals()

Models may optionally define

```python
def calibration_residuals(params, data):
```

This allows complete customization of the calibration objective.

Most users can rely on UQDash's built-in residual calculation.

---

## Additional Helper Functions

Any additional functions may be included.

Examples

```python
plot_model()

steady_state()

jacobian()

basic_reproduction_number()

compute_observables()
```

These do not interfere with UQDash.

---

# Parameter Bounds

Parameter bounds determine the search space for

* sensitivity analysis
* uncertainty propagation
* calibration

Example

```python
PARAMETERS = {

    "alpha": {
        "nominal": 2.0,
        "bounds": [1.0, 3.0],
    }

}
```

A common strategy is to define bounds as a multiple of the nominal value.

UQDash will provide utilities for automatically generating bounds from user-specified multipliers soon.

---

# Simulation Requirements

The simulation function must return a pandas DataFrame.

Example

```python
return pd.DataFrame({
    "time": solution.t,
    "Tumor": solution.y[0],
    "Immune": solution.y[1],
})
```

The first column must be named

```text
time
```

All remaining columns are interpreted as state variables.

---

# Calibration Data Format

Calibration and validation data must be supplied as CSV files.

Observed variables should be named

```text
observed_<state_name>
```

For example

| time | observed_Tumor | observed_Immune |
| ---: | -------------: | --------------: |
|    0 |           1000 |             500 |
|    5 |           1200 |             430 |

The state name must exactly match the corresponding simulation output column.

---

# Solver Compatibility

The simulation function offers any SciPy solver.

Examples include

* RK45
* RK23
* DOP853
* Radau
* BDF
* LSODA

If the solver argument is omitted, UQDash will use the model's default.

---

# Quantity of Interest (QoI)

The QoI is central to uncertainty quantification.

Choose a quantity that answers the scientific question.

Examples

* Final tumor burden
* Maximum viral load
* Peak concentration
* Time to equilibrium
* Maximum immune response
* Area under the curve (AUC)
* Total drug administered

Different QoIs may lead to different sensitivity rankings and uncertainty estimates.

---

# Best Practices

* Use descriptive parameter names.
* Ensure the simulation returns a valid DataFrame.
* Verify the model under nominal parameters before running uncertainty analyses.
* Calibrate only influential parameters whenever possible.
* Use validation data that were not used during calibration.

---

# Example Project Structure

```
examples/
    logistic_model.py
    calibration.csv
    validation.csv

    tnbc_model.py
    tnbc_calibration.csv
    tnbc_validation.csv
```

Keeping models and associated datasets together simplifies reproducibility.

---

# Example Minimal Model

```python
PARAMETERS = {
    "r": {
        "nominal": 0.5,
        "bounds": [0.1, 1.0],
    },
    "K": {
        "nominal": 100.0,
        "bounds": [50.0, 200.0],
    },
}

INITIAL_CONDITIONS = {
    "Population": 10.0,
}

STATE_NAMES = [
    "Population",
]


def rhs(t, y, params):

    population = y[0]

    dPopulation = (
        params["r"]
        * population
        * (1 - population / params["K"])
    )

    return [dPopulation]


def simulate(
    params,
    t_span=(0.0, 20.0),
    t_eval=None,
    method="RK45",
):

    import numpy as np
    import pandas as pd
    from scipy.integrate import solve_ivp

    if t_eval is None:
        t_eval = np.linspace(*t_span, 200)

    solution = solve_ivp(
        lambda t, y: rhs(t, y, params),
        t_span=t_span,
        y0=[INITIAL_CONDITIONS["Population"]],
        t_eval=t_eval,
        method=method,
    )

    return pd.DataFrame({
        "time": solution.t,
        "Population": solution.y[0],
    })


def evaluate(params):

    simulation = simulate(params)

    return simulation["Population"].iloc[-1]
```

This example contains every required component needed to use all major features of UQDash.

---

# Next Steps

Once your model satisfies this interface, it can immediately be analyzed using every major component of UQDash, including simulation, sensitivity analysis, uncertainty propagation, calibration, validation, and automated report generation.

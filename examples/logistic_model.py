import numpy as np
from scipy.integrate import solve_ivp


PARAMETERS = {
    "r": {"bounds": [0.1, 1.0], "nominal": 0.55},
    "K": {"bounds": [50.0, 1000.0], "nominal": 125.0},
    "x0": {"bounds": [1.0, 20.0], "nominal": 10.0},
}


def logistic_growth(t, x, r, K):
    return r * x[0] * (1 - x[0] / K)

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

def evaluate(params):
    """
    Required UQdash function.

    Input:
        params: dict of parameter values

    Output:
        scalar quantity of interest
    """
    r = params["r"]
    K = params["K"]
    x0 = params["x0"]

    T = 10.0

    sol = solve_ivp(
        lambda t, x: logistic_growth(t, x, r, K),
        t_span=(0, T),
        y0=[x0],
        t_eval=np.linspace(0, T, 200),
    )

    return sol.y[0, -1]

def calibration_residuals(params, data):
    """
    Compute residuals between the logistic model and observed data.
    """
    import numpy as np

    r = params["r"]
    K = params["K"]

    N0 = 50.0

    residuals = []

    for _, row in data.iterrows():
        t = row["time"]
        observed = row["observed_population"]

        prediction = K / (
            1
            + ((K - N0) / N0) * np.exp(-r * t)
        )

        residuals.append(prediction - observed)

    return residuals
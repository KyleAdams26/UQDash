"""
Example TNBC model for UQDash.

Converted from the MATLAB TNBC model with 5 state variables and 39 parameters.

States:
    M2 : M2 macrophages
    F  : cancer-associated fibroblasts
    B  : TNBC cells
    Tc : cytotoxic T cells
    Tr : regulatory T cells

This file supports:
    - model simulation
    - sensitivity analysis
    - parameter analysis
    - uncertainty propagation
    - calibration / validation hooks

Bounds are generated automatically from nominal values:

    lower bound = LOWER_MULTIPLIER * nominal
    upper bound = UPPER_MULTIPLIER * nominal

By default:
    LOWER_MULTIPLIER = 0.5
    UPPER_MULTIPLIER = 1.5
"""

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp


# ------------------------------------------------------------
# Global bound multipliers.
# ------------------------------------------------------------
LOWER_MULTIPLIER = 0.5
UPPER_MULTIPLIER = 1.5


# ------------------------------------------------------------
# Parameters whose upper bounds should be capped at 1.
#
# These are dimensionless inhibition/modulation parameters where values
# above 1 are usually not meaningful.
# ------------------------------------------------------------
CAP_UPPER_AT_ONE = {
    "a2CB",
    "aBCB",
    "aRCB",
    "aRC",
}


# ------------------------------------------------------------
# Nominal parameter values from the MATLAB setParameters() file.
# ------------------------------------------------------------
NOMINAL_PARAMETERS = {
    "aB2": 10000.0,
    "bB2": 8360.0,
    "aF2": 1.2,
    "bF2": 2890.0,
    "g2": 0.005,
    "aC2": 3.0,
    "bC2": 267200.0,
    "d2": 0.116,
    "sF": 0.000998,
    "KF": 65500.0,
    "dF": 0.00175,
    "pB": 0.00998,
    "KB": 262000.0,
    "a2B": 0.318,
    "b2B": 86000.0,
    "aFB": 1.63,
    "bFB": 2890.0,
    "dB": 0.0005,
    "aCB": 29.0,
    "bCB": 267200.0,
    "a2CB": 0.758,
    "b2CB": 86000.0,
    "aBCB": 0.821,
    "bBCB": 8360.0,
    "aRCB": 0.545,
    "bRCB": 43600.0,
    "pC": 1.13,
    "KC": 223000.0,
    "a2C": 7.0,
    "b2C": 17200000.0,
    "aRC": 0.946,
    "bRC": 43600.0,
    "dC": 0.406,
    "sR": 583.33,
    "a2R": 0.471,
    "b2R": 86000.0,
    "aBR": 1.063,
    "bBR": 8360.0,
    "dR": 0.0630,
}


def make_parameter_entry(name: str, nominal: float) -> dict:
    """
    Create a UQDash parameter entry from a nominal value.
    """
    lower = LOWER_MULTIPLIER * nominal
    upper = UPPER_MULTIPLIER * nominal

    # Cap selected inhibitory/modulatory parameters at 1.
    if name in CAP_UPPER_AT_ONE:
        upper = min(upper, 1.0)

    # Avoid zero-width bounds if a nominal value is ever zero.
    if lower == upper:
        upper = lower + 1e-12

    return {
        "nominal": nominal,
        "bounds": [lower, upper],
    }


# ------------------------------------------------------------
# UQDash-required parameter dictionary.
# ------------------------------------------------------------
PARAMETERS = {
    name: make_parameter_entry(name, nominal)
    for name, nominal in NOMINAL_PARAMETERS.items()
}


# ------------------------------------------------------------
# Initial conditions from MATLAB setInitialConditions().
# ------------------------------------------------------------
INITIAL_CONDITIONS = {
    "M2": 21500.0,
    "F": 722.0,
    "B": 2090.0,
    "Tc": 66800.0,
    "Tr": 10900.0,
}


def nominal_params() -> dict:
    """
    Return a parameter dictionary using nominal values.
    """
    return {
        name: info["nominal"]
        for name, info in PARAMETERS.items()
    }


def rhs(t, c, p):
    """
    Right-hand side of the TNBC ODE model.

    State order:
        c[0] = M2
        c[1] = F
        c[2] = B
        c[3] = Tc
        c[4] = Tr
    """
    M2 = c[0]
    F = c[1]
    B = c[2]
    Tc = c[3]
    Tr = c[4]

    # ------------------------------------------------------------
    # Pathway terms from the MATLAB model.
    # ------------------------------------------------------------
    aPath = p["aF2"] * F / (p["bF2"] + F)
    bPath = p["a2R"] * M2 / (p["b2R"] + M2)
    c_lPath = p["aB2"] * B / (p["bB2"] + B)
    d_mPath = p["sF"] * B * (1.0 - F / p["KF"])
    ePath = p["g2"] * M2
    fPath = p["a2B"] * M2 / (p["b2B"] + M2)
    gPath = p["aFB"] * F / (p["bFB"] + F)
    hPath = p["aC2"] * Tc / (p["bC2"] + Tc)
    iPath = p["d2"] * M2
    jPath = p["pB"] * B * (1.0 - B / p["KB"])
    kPath = p["dF"] * F
    nPath = p["a2C"] * M2 / (p["b2C"] + M2)
    oPath = p["a2CB"] * M2 / (p["b2CB"] + M2)
    pPath = p["aBR"] * B / (p["bBR"] + B)
    qPath = p["pC"] * Tc * (1.0 - Tc / p["KC"])
    rPath = p["aBCB"] * B / (p["bBCB"] + B)
    sPath = p["sR"]
    tPath = p["aCB"] * Tc / (p["bCB"] + Tc)
    uPath = p["dB"] * B
    vPath = p["dC"] * Tc
    wPath = p["aRCB"] * Tr / (p["bRCB"] + Tr)
    xPath = p["dR"] * Tr
    yPath = p["aRC"] * Tr / (p["bRC"] + Tr)

    # ------------------------------------------------------------
    # Dynamics from the MATLAB odefun().
    # ------------------------------------------------------------
    dM2dt = c_lPath * (1.0 + aPath) - ePath * (1.0 + hPath) - iPath

    dFdt = d_mPath - kPath

    dBdt = (
        jPath * (1.0 + fPath) * (1.0 + gPath)
        - uPath
        * (
            1.0
            + tPath
            * (1.0 - rPath)
            * (1.0 - oPath)
            * (1.0 - wPath)
        )
    )

    dTcdt = qPath * (1.0 + nPath) * (1.0 - yPath) - vPath

    dTrdt = sPath * (1.0 + bPath) * (1.0 + pPath) - xPath

    return [dM2dt, dFdt, dBdt, dTcdt, dTrdt]


def simulate(params, t_span=(0.0, 168.0), t_eval=None, method="RK45"):
    """
    Simulate the TNBC model and return a trajectory DataFrame.

    This function is used by the Model Simulation tab.
    """
    if t_eval is None:
        t_eval = np.linspace(t_span[0], t_span[1], 300)

    y0 = [
        INITIAL_CONDITIONS["M2"],
        INITIAL_CONDITIONS["F"],
        INITIAL_CONDITIONS["B"],
        INITIAL_CONDITIONS["Tc"],
        INITIAL_CONDITIONS["Tr"],
    ]

    sol = solve_ivp(
        fun=lambda t, y: rhs(t, y, params),
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        method=method,
        rtol=1e-6,
        atol=1e-8,
    )

    if not sol.success:
        raise RuntimeError(sol.message)

    return pd.DataFrame({
        "time": sol.t,
        "M2": sol.y[0],
        "CAF": sol.y[1],
        "TNBC": sol.y[2],
        "Tc": sol.y[3],
        "Treg": sol.y[4],
    })


def evaluate(params):
    """
    Required UQDash scalar QoI function.

    Here the QoI is final TNBC burden at 168 hours.
    """
    simulation_df = simulate(
        params=params,
        t_span=(0.0, 168.0),
        t_eval=np.linspace(0.0, 168.0, 250),
        method="RK45",
    )

    return float(simulation_df["TNBC"].iloc[-1])


def validation_predictions(params, data):
    """
    Compute model predictions for validation data.

    Expected validation CSV column:
        time

    This returns TNBC burden at each requested time.
    """
    times = data["time"].to_numpy(dtype=float)

    simulation_df = simulate(
        params=params,
        t_span=(float(times.min()), float(times.max())),
        t_eval=times,
        method="RK45",
    )

    return simulation_df["TNBC"].to_numpy()


def calibration_residuals(params, data):
    """
    Compute residuals for calibration.

    Expected calibration CSV columns:
        time, observed_tnbc

    Residual convention:
        prediction - observed
    """
    if "observed_tnbc" not in data.columns:
        raise ValueError(
            "TNBC calibration data must contain columns: time, observed_tnbc"
        )

    predictions = validation_predictions(params, data)
    observed = data["observed_tnbc"].to_numpy(dtype=float)

    return predictions - observed
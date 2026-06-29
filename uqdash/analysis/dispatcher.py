"""
Dispatch sensitivity-analysis methods by name.
"""

from uqdash.analysis.sobol import run_sobol
from uqdash.analysis.morris import run_morris
from uqdash.analysis.efast import run_efast


def run_sensitivity_analysis(
    method: str,
    model_module,
    n_samples: int = 512,
    frozen_parameters: list[str] | None = None,
    seed: int = 1,
):
    """Dispatch sensitivity analysis by method name."""
    if method == "Sobol":
        return run_sobol(
            model_module=model_module,
            n_samples=n_samples,
            frozen_parameters=frozen_parameters,
            seed=seed,
        )

    if method == "Morris":
        return run_morris(
            model_module=model_module,
            n_samples=n_samples,
            frozen_parameters=frozen_parameters,
            seed=seed,
        )

    if method == "eFAST":
        return run_efast(
            model_module=model_module,
            n_samples=n_samples,
            frozen_parameters=frozen_parameters,
            seed=seed,
        )

    raise ValueError(f"Unsupported sensitivity analysis method: {method}")
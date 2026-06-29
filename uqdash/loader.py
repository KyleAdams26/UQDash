import importlib.util
from pathlib import Path


def load_model_from_path(path):
    """
    Dynamically load a Python model file.

    The file must define:
        PARAMETERS
        evaluate(params)
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")

    spec = importlib.util.spec_from_file_location("user_model", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    validate_model(module)

    return module


def validate_model(module):
    if not hasattr(module, "PARAMETERS"):
        raise ValueError("Model file must define PARAMETERS.")

    if not hasattr(module, "evaluate"):
        raise ValueError("Model file must define evaluate(params).")

    if not callable(module.evaluate):
        raise ValueError("evaluate must be a function.")

    for name, info in module.PARAMETERS.items():
        if "bounds" not in info:
            raise ValueError(f"Parameter {name} is missing bounds.")

        bounds = info["bounds"]

        if len(bounds) != 2:
            raise ValueError(f"Parameter {name} bounds must have length 2.")

        if bounds[0] >= bounds[1]:
            raise ValueError(f"Parameter {name} lower bound must be < upper bound.")
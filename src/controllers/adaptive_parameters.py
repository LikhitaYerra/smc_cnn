ADAPTIVE_SMC_PARAMETERS = {
    "normal": {
        "lambda_x": 2.0,
        "lambda_y": 2.0,
        "lambda_theta": 1.0,
        "k_v": 0.3,
        "k_omega": 0.8,
        "phi": 0.5,
        "max_v": 0.6,
        "max_omega": 1.5,
        "omega_smoothing": 0.95,
    },

    # More balanced: still smoother than classical, but not too weak
    "noise": {
        "lambda_x": 2.0,
        "lambda_y": 2.1,
        "lambda_theta": 0.95,
        "k_v": 0.30,
        "k_omega": 0.78,
        "phi": 0.58,
        "max_v": 0.6,
        "max_omega": 1.35,
        "omega_smoothing": 0.965,
    },

    # Slightly less aggressive than previous version
    "disturbance": {
        "lambda_x": 2.15,
        "lambda_y": 2.30,
        "lambda_theta": 1.05,
        "k_v": 0.33,
        "k_omega": 0.88,
        "phi": 0.52,
        "max_v": 0.65,
        "max_omega": 1.55,
        "omega_smoothing": 0.945,
    },

    # Keep better tracking but reduce effort a little
    "slip": {
        "lambda_x": 2.20,
        "lambda_y": 2.20,
        "lambda_theta": 1.00,
        "k_v": 0.35,
        "k_omega": 0.86,
        "phi": 0.62,
        "max_v": 0.68,
        "max_omega": 1.50,
        "omega_smoothing": 0.96,
    },

    # Stronger than previous combined version, but still smoother than classical
    "combined": {
        "lambda_x": 2.15,
        "lambda_y": 2.35,
        "lambda_theta": 1.0,
        "k_v": 0.35,
        "k_omega": 0.88,
        "phi": 0.62,
        "max_v": 0.66,
        "max_omega": 1.35,
        "omega_smoothing": 0.965,
    },
}


def get_adaptive_smc_parameters(scenario: str) -> dict:
    if scenario not in ADAPTIVE_SMC_PARAMETERS:
        raise ValueError(f"Unknown scenario: {scenario}")

    return ADAPTIVE_SMC_PARAMETERS[scenario].copy()
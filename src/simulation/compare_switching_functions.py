import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.simulation.simulate_classical_smc import run_classical_smc_simulation


def main():
    configs = [
        ("sign", 0.5, 0.95),
        ("sat", 0.5, 0.95),
        ("tanh", 0.5, 0.95),
    ]

    for switching_type, phi, omega_smoothing in configs:
        run_classical_smc_simulation(
            switching_type=switching_type,
            phi=phi,
            omega_smoothing=omega_smoothing,
        )


if __name__ == "__main__":
    main()
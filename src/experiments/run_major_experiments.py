"""Run classical, CNN-adaptive, oracle, fuzzy, and RL-adaptive SMC across all scenarios."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.controllers.adaptive_parameters import get_adaptive_smc_parameters
from src.controllers.adaptive_smc_controller import AdaptiveSlidingModeController
from src.controllers.fuzzy_smc_controller import FuzzySlidingModeController
from src.controllers.rl_adaptive_smc_controller import RLAdaptiveSlidingModeController
from src.controllers.smc_controller import SlidingModeController
from src.cnn.predictor import CNNEnvironmentPredictor
from src.data_generation.environment_generator import EnvironmentMapGenerator
from src.simulation.run_episode import ScenarioConfig, SimulationConfig, default_scenarios, run_tracking_episode
from src.utils.logger import save_simulation_log


def _classical_factory():
    return SlidingModeController(
        lambda_x=2.0,
        lambda_y=2.0,
        lambda_theta=1.0,
        k_v=0.3,
        k_omega=0.8,
        phi=0.5,
        max_v=0.6,
        max_omega=1.5,
        switching_type="tanh",
        omega_smoothing=0.95,
    )


def run_controller_batch(controller_key: str):
    scenarios = default_scenarios()
    log_dir_names = {
        "classical_smc": "classical_smc_issues",
        "cnn_adaptive_smc": "adaptive_smc",
        "oracle_adaptive_smc": "oracle_adaptive_smc",
        "fuzzy_smc": "fuzzy_smc",
        "rl_adaptive_smc": "rl_adaptive_smc",
    }
    log_dir = Path(f"results/logs/{log_dir_names.get(controller_key, controller_key)}")
    log_dir.mkdir(parents=True, exist_ok=True)

    if controller_key == "classical_smc":
        for scenario in scenarios:
            log = run_tracking_episode(_classical_factory, scenario)
            save_simulation_log(log, str(log_dir / f"log_{scenario.name}.csv"))
            print(f"[classical_smc] {scenario.name} done")

    elif controller_key == "cnn_adaptive_smc":
        predictor = CNNEnvironmentPredictor(model_path="models/cnn_environment_classifier.pt")
        map_generator = EnvironmentMapGenerator(map_size=64, seed=42)
        state = {"prediction": {"scenario": "normal", "confidence": 0.0}}

        def factory():
            return AdaptiveSlidingModeController(
                initial_params=get_adaptive_smc_parameters("normal"),
                switching_type="tanh",
            )

        def on_step(i, _t, ctx):
            if i % 100 == 0:
                env_map = map_generator.generate(ctx["scenario"])
                state["prediction"] = predictor.predict(env_map)
                ctx["controller"].update_parameters(
                    get_adaptive_smc_parameters(state["prediction"]["scenario"])
                )

        def extra_fields(_i, _t, _ctx):
            return {
                "predicted_scenario": state["prediction"]["scenario"],
                "cnn_confidence": state["prediction"]["confidence"],
            }

        for scenario in scenarios:
            state["prediction"] = predictor.predict(map_generator.generate(scenario.name))
            log = run_tracking_episode(
                factory,
                scenario,
                on_step=on_step,
                extra_log_fields=extra_fields,
            )
            save_simulation_log(log, str(log_dir / f"log_{scenario.name}.csv"))
            print(f"[cnn_adaptive_smc] {scenario.name} done")

    elif controller_key == "oracle_adaptive_smc":
        for scenario in scenarios:
            preset = scenario.name

            def factory(p=preset):
                controller = AdaptiveSlidingModeController(
                    initial_params=get_adaptive_smc_parameters(p),
                    switching_type="tanh",
                )
                return controller

            def on_step(i, _t, ctx, p=preset):
                if i % 100 == 0:
                    ctx["controller"].update_parameters(get_adaptive_smc_parameters(p))

            log = run_tracking_episode(factory, scenario, on_step=on_step)
            save_simulation_log(log, str(log_dir / f"log_{scenario.name}.csv"))
            print(f"[oracle_adaptive_smc] {scenario.name} done")

    elif controller_key == "fuzzy_smc":
        for scenario in scenarios:
            log = run_tracking_episode(lambda: FuzzySlidingModeController(switching_type="tanh"), scenario)
            save_simulation_log(log, str(log_dir / f"log_{scenario.name}.csv"))
            print(f"[fuzzy_smc] {scenario.name} done")

    elif controller_key == "rl_adaptive_smc":
        for scenario in scenarios:
            controller = RLAdaptiveSlidingModeController()
            controller.set_scenario_flags(scenario.enable_noise, scenario.enable_slip)

            def factory(c=controller):
                c.reset()
                c.set_scenario_flags(scenario.enable_noise, scenario.enable_slip)
                return c

            log = run_tracking_episode(factory, scenario)
            save_simulation_log(log, str(log_dir / f"log_{scenario.name}.csv"))
            print(f"[rl_adaptive_smc] {scenario.name} done")

    else:
        raise ValueError(f"Unknown controller: {controller_key}")


def main():
    controllers = [
        "classical_smc",
        "fuzzy_smc",
        "cnn_adaptive_smc",
        "oracle_adaptive_smc",
    ]

    rl_policy = Path("models/rl_smc_parameter_policy_state.pt")
    if not rl_policy.exists():
        rl_policy = Path("models/rl_smc_parameter_policy.zip")
    if rl_policy.exists():
        controllers.append("rl_adaptive_smc")
    else:
        print("RL policy not found; skipping rl_adaptive_smc (train with src/rl/train_rl_policy.py)")

    for controller in controllers:
        print(f"\n=== Running {controller} ===")
        run_controller_batch(controller)

    print("\nAll requested controller batches completed.")


if __name__ == "__main__":
    main()

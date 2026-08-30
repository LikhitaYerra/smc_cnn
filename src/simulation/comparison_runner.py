"""Run headless controller comparisons for presentation benchmarks."""

from __future__ import annotations

import copy

from src.simulation.simulation_engine import SimulationConfig, SimulationEngine, CONTROLLER_MODES

MODE_LABELS = {
    "classical": "Classical SMC",
    "cnn_adaptive": "CNN-Adaptive SMC",
    "rl_agent": "RL Agent (PPO)",
}

MODE_COLORS = {
    "classical": "#ff6b6b",
    "cnn_adaptive": "#00d4aa",
    "rl_agent": "#7c5cff",
}


def run_single_benchmark(
    controller_mode: str,
    scenario_name: str = "combined",
    trajectory_type: str = "straight",
    enable_noise: bool = True,
    enable_disturbance: bool = True,
    enable_slip: bool = True,
    total_time: float = 15.0,
) -> dict:
    config = SimulationConfig(
        controller_mode=controller_mode,
        scenario_name=scenario_name,
        trajectory_type=trajectory_type,
        enable_noise=enable_noise,
        enable_disturbance=enable_disturbance,
        enable_slip=enable_slip,
        total_time=total_time,
    )

    engine = SimulationEngine()
    engine.reset(config)
    engine.resume()

    while not engine.state.finished:
        engine.step()

    metrics = copy.deepcopy(engine.state.metrics)
    path = [
        {"x": p["x"], "y": p["y"], "t": p.get("t", 0)}
        for p in engine.state.path_history[::5]
    ]
    return {
        "controller_mode": controller_mode,
        "label": MODE_LABELS.get(controller_mode, controller_mode),
        "color": MODE_COLORS.get(controller_mode, "#888"),
        "metrics": metrics,
        "final_error": engine.state.tracking_error,
        "scenario": scenario_name,
        "path_history": path,
    }


def run_dual_comparison(
    scenario_name: str = "combined",
    mode_a: str = "classical",
    mode_b: str = "cnn_adaptive",
    **kwargs,
) -> dict:
    a = run_single_benchmark(mode_a, scenario_name=scenario_name, **kwargs)
    b = run_single_benchmark(mode_b, scenario_name=scenario_name, **kwargs)
    return {"mode_a": a, "mode_b": b, "scenario": scenario_name}


def run_controller_comparison(
    scenario_name: str = "combined",
    trajectory_type: str = "straight",
    enable_noise: bool = True,
    enable_disturbance: bool = True,
    enable_slip: bool = True,
    total_time: float = 15.0,
) -> dict:
    results = []
    for mode in CONTROLLER_MODES:
        results.append(
            run_single_benchmark(
                controller_mode=mode,
                scenario_name=scenario_name,
                trajectory_type=trajectory_type,
                enable_noise=enable_noise,
                enable_disturbance=enable_disturbance,
                enable_slip=enable_slip,
                total_time=total_time,
            )
        )

    # Rank by RMSE (lower is better)
    ranked = sorted(results, key=lambda r: r["metrics"].get("rmse_tracking_error", 999))
    for i, r in enumerate(ranked):
        r["rank"] = i + 1

    return {
        "scenario": scenario_name,
        "trajectory": trajectory_type,
        "results": results,
        "winner": ranked[0]["controller_mode"] if ranked else None,
    }

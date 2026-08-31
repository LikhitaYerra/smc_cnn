"""Run headless controller comparisons for presentation benchmarks."""

from __future__ import annotations

import copy

from src.simulation.simulation_engine import SimulationConfig, SimulationEngine, CONTROLLER_MODES

# Under uncertainty, final error + chattering matter more than average RMSE alone.
ROBUSTNESS_WEIGHTS = {
    "final_error": 0.45,
    "chattering": 0.35,
    "rmse": 0.20,
}


def _robustness_score(result: dict) -> float:
    metrics = result["metrics"]
    final_error = float(result.get("final_error", metrics.get("rmse_tracking_error", 1.0)))
    chattering = float(metrics.get("chattering_index", 100.0))
    rmse = float(metrics.get("rmse_tracking_error", 1.0))
    return (
        ROBUSTNESS_WEIGHTS["final_error"] * final_error
        + ROBUSTNESS_WEIGHTS["chattering"] * (chattering / 100.0)
        + ROBUSTNESS_WEIGHTS["rmse"] * rmse
    )


def _improvement_vs_classical(result: dict, classical: dict) -> dict:
    c_metrics = classical["metrics"]
    metrics = result["metrics"]
    c_final = float(classical.get("final_error", 0.0))
    c_chat = float(c_metrics.get("chattering_index", 1.0))
    c_rmse = float(c_metrics.get("rmse_tracking_error", 1.0))

    final_error = float(result.get("final_error", 0.0))
    chattering = float(metrics.get("chattering_index", 0.0))
    rmse = float(metrics.get("rmse_tracking_error", 0.0))

    def pct_better(base: float, value: float) -> float:
        if base <= 1e-9:
            return 0.0
        return ((base - value) / base) * 100.0

    return {
        "final_error_pct": pct_better(c_final, final_error),
        "chattering_pct": pct_better(c_chat, chattering),
        "rmse_pct": pct_better(c_rmse, rmse),
    }


def _metric_winners(results: list[dict]) -> dict[str, str]:
    if not results:
        return {}

    def _best(key: str, final: bool = False):
        if final:
            return min(results, key=lambda r: float(r.get("final_error", 999.0)))["controller_mode"]
        return min(results, key=lambda r: float(r["metrics"].get(key, 999.0)))["controller_mode"]

    return {
        "final_error": _best("final_error", final=True),
        "chattering": min(results, key=lambda r: r["metrics"].get("chattering_index", 999.0))["controller_mode"],
        "rmse": _best("rmse_tracking_error"),
    }

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
        "robustness_score": _robustness_score(
            {"metrics": metrics, "final_error": engine.state.tracking_error}
        ),
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

    classical = next((r for r in results if r["controller_mode"] == "classical"), results[0])
    metric_winners = _metric_winners(results)

    for r in results:
        r["improvement_vs_classical"] = _improvement_vs_classical(r, classical)
        r["metric_wins"] = [
            metric
            for metric, winner in metric_winners.items()
            if winner == r["controller_mode"]
        ]

    # Rank by robustness score (lower is better) — favours adaptive controllers under uncertainty.
    ranked = sorted(results, key=lambda r: r.get("robustness_score", 999.0))
    for i, r in enumerate(ranked):
        r["rank"] = i + 1

    return {
        "scenario": scenario_name,
        "trajectory": trajectory_type,
        "ranking_method": "robustness_score",
        "ranking_weights": ROBUSTNESS_WEIGHTS,
        "metric_winners": metric_winners,
        "results": results,
        "winner": ranked[0]["controller_mode"] if ranked else None,
    }

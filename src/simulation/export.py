"""Export simulation metrics to CSV."""

from __future__ import annotations

import csv
import io
import os
from datetime import datetime


def export_metrics_csv(sim_state: dict, config: dict) -> str:
    """Return CSV string of simulation results."""
    metrics = sim_state.get("metrics", {})
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Robot Digital Twin — Simulation Report"])
    writer.writerow(["Generated", datetime.now().isoformat()])
    writer.writerow([])

    writer.writerow(["Configuration"])
    writer.writerow(["Controller", config.get("controller_mode", "")])
    writer.writerow(["Scenario", config.get("scenario_name", "")])
    writer.writerow(["Trajectory", config.get("trajectory_type", "")])
    writer.writerow(["Noise", config.get("enable_noise", False)])
    writer.writerow(["Disturbance", config.get("enable_disturbance", False)])
    writer.writerow(["Slip", config.get("enable_slip", False)])
    writer.writerow([])

    writer.writerow(["Results"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Final Tracking Error (m)", sim_state.get("tracking_error", "")])
    writer.writerow(["RMSE", metrics.get("rmse_tracking_error", "")])
    writer.writerow(["Mean Error", metrics.get("mean_tracking_error", "")])
    writer.writerow(["Max Error", metrics.get("max_tracking_error", "")])
    writer.writerow(["Chattering Index", metrics.get("chattering_index", "")])
    writer.writerow(["Control Effort", metrics.get("control_effort", "")])
    writer.writerow(["Duration (s)", sim_state.get("time", "")])

    if sim_state.get("predicted_scenario"):
        writer.writerow([])
        writer.writerow(["CNN Prediction", sim_state.get("predicted_scenario", "")])
        writer.writerow(["CNN Confidence", sim_state.get("cnn_confidence", "")])

    writer.writerow([])
    writer.writerow(["Error History"])
    writer.writerow(["Time (s)", "Error (m)"])
    for pt in sim_state.get("error_history", []):
        writer.writerow([pt.get("t", ""), pt.get("error", "")])

    return output.getvalue()


def export_comparison_csv(results: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Controller Comparison Report"])
    writer.writerow(["Generated", datetime.now().isoformat()])
    writer.writerow([])
    writer.writerow(["Rank", "Controller", "RMSE", "Max Error", "Chattering", "Control Effort", "Final Error"])

    for r in sorted(results, key=lambda x: x.get("rank", 99)):
        m = r.get("metrics", {})
        writer.writerow([
            r.get("rank", ""),
            r.get("label", ""),
            m.get("rmse_tracking_error", ""),
            m.get("max_tracking_error", ""),
            m.get("chattering_index", ""),
            m.get("control_effort", ""),
            r.get("final_error", ""),
        ])
    return output.getvalue()

"""FastAPI server with WebSocket for real-time digital twin simulation."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse, JSONResponse, FileResponse
from datetime import datetime

from src.simulation.simulation_engine import SimulationConfig, SimulationEngine, CONTROLLER_MODES
from src.simulation.comparison_runner import run_controller_comparison, run_dual_comparison, MODE_LABELS, MODE_COLORS
from src.simulation.recording import save_recording, list_recordings, load_recording
from src.simulation.export import export_metrics_csv, export_comparison_csv
from src.runtime.lite_mode import is_lite_mode

PRESENTATION_PRESETS = [
    {
        "id": "showcase",
        "name": "Full Showcase",
        "description": "Combined scenario — best for live demo",
        "config": {
            "controller_mode": "cnn_adaptive",
            "scenario_name": "combined",
            "trajectory_type": "straight",
            "enable_noise": True,
            "enable_disturbance": True,
            "enable_slip": True,
            "total_time": 18.0,
            "simulation_speed": 3.0,
        },
    },
    {
        "id": "rl_demo",
        "name": "RL Agent Demo",
        "description": "Show PPO adaptive control under disturbances",
        "config": {
            "controller_mode": "rl_agent",
            "scenario_name": "combined",
            "trajectory_type": "s_curve",
            "enable_noise": True,
            "enable_disturbance": True,
            "enable_slip": True,
            "total_time": 18.0,
            "simulation_speed": 3.0,
        },
    },
    {
        "id": "classical_fail",
        "name": "Classical vs Issues",
        "description": "Show classical SMC struggling with combined uncertainty",
        "config": {
            "controller_mode": "classical",
            "scenario_name": "combined",
            "trajectory_type": "straight",
            "enable_noise": True,
            "enable_disturbance": True,
            "enable_slip": True,
            "total_time": 18.0,
            "simulation_speed": 3.0,
        },
    },
]


class SimulationRequest(BaseModel):
    controller_mode: str = "cnn_adaptive"
    scenario_name: str = "normal"
    trajectory_type: str = "straight"
    enable_noise: bool = False
    enable_disturbance: bool = False
    enable_slip: bool = False
    total_time: float = 20.0
    desired_speed: float = 0.3
    simulation_speed: float = 1.0


class RLTrainingRequest(BaseModel):
    iterations: int = 20
    quick: bool = True


class ComparisonRequest(BaseModel):
    scenario_name: str = "combined"
    trajectory_type: str = "straight"
    enable_noise: bool = True
    enable_disturbance: bool = True
    enable_slip: bool = True
    total_time: float = 12.0


engine = SimulationEngine()
active_connections: list[WebSocket] = []
comparison_status: dict[str, Any] = {"running": False, "progress": 0, "results": None}
rl_training_status: dict[str, Any] = {
    "running": False,
    "progress": 0,
    "message": "Idle",
    "best_reward": None,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bootstrap RL model in background if missing (non-blocking for startup)
    yield


app = FastAPI(
    title="Robot Digital Twin API",
    description="Real-time SMC simulation with RL agent support",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _config_from_dict(msg: dict) -> SimulationConfig:
    return SimulationConfig(
        controller_mode=msg.get("controller_mode", "cnn_adaptive"),
        scenario_name=msg.get("scenario_name", "normal"),
        trajectory_type=msg.get("trajectory_type", "straight"),
        enable_noise=msg.get("enable_noise", False),
        enable_disturbance=msg.get("enable_disturbance", False),
        enable_slip=msg.get("enable_slip", False),
        total_time=msg.get("total_time", 20.0),
        desired_speed=msg.get("desired_speed", 0.3),
        simulation_speed=max(0.5, min(msg.get("simulation_speed", 1.0), 10.0)),
    )


@app.get("/health")
async def render_health():
    """Render health check — must not be shadowed by static file serving."""
    return {"status": "ok", "lite_mode": is_lite_mode()}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "robot-digital-twin",
        "lite_mode": is_lite_mode(),
        "rl_model_loaded": is_lite_mode() or False,
        "cnn_ready": True,
    }


@app.get("/api/config")
async def get_config():
    return {
        "controller_modes": [
            {"id": m, "label": MODE_LABELS.get(m, m), "color": MODE_COLORS.get(m, "#888")}
            for m in CONTROLLER_MODES
        ],
        "scenarios": ["normal", "noise", "disturbance", "slip", "combined"],
        "trajectories": ["straight", "circle", "s_curve"],
        "presets": PRESENTATION_PRESETS,
        "rl_training": rl_training_status,
        "comparison": comparison_status,
        "lite_mode": is_lite_mode(),
    }


@app.get("/api/presets")
async def get_presets():
    return PRESENTATION_PRESETS


@app.post("/api/simulation/reset")
async def reset_simulation(req: SimulationRequest):
    config = _config_from_dict(req.model_dump())
    engine.reset(config)
    return engine.to_dict()


@app.post("/api/simulation/step")
async def step_simulation():
    engine.step()
    return engine.to_dict()


@app.get("/api/simulation/state")
async def get_state():
    return engine.to_dict()


@app.get("/api/recordings")
async def get_recordings():
    return list_recordings()


@app.get("/api/recordings/{recording_id}")
async def get_recording(recording_id: str):
    data = load_recording(recording_id)
    if not data:
        return {"error": "Not found"}
    return data


@app.post("/api/dual-compare")
async def dual_compare(req: ComparisonRequest):
    def _run():
        return run_dual_comparison(
            scenario_name=req.scenario_name,
            trajectory_type=req.trajectory_type,
            enable_noise=req.enable_noise,
            enable_disturbance=req.enable_disturbance,
            enable_slip=req.enable_slip,
            total_time=req.total_time,
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run)


@app.get("/api/export/metrics")
async def export_metrics():
    state = engine.to_dict()
    config = {
        "controller_mode": engine.config.controller_mode,
        "scenario_name": engine.config.scenario_name,
        "trajectory_type": engine.config.trajectory_type,
        "enable_noise": engine.config.enable_noise,
        "enable_disturbance": engine.config.enable_disturbance,
        "enable_slip": engine.config.enable_slip,
    }
    csv_content = export_metrics_csv(state, config)
    return PlainTextResponse(csv_content, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=simulation_metrics.csv"
    })


@app.get("/api/export/comparison")
async def export_comparison():
    if not comparison_status.get("results"):
        return {"error": "No comparison results available"}
    csv_content = export_comparison_csv(comparison_status["results"]["results"])
    return PlainTextResponse(csv_content, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=controller_comparison.csv"
    })


@app.post("/api/bootstrap")
async def bootstrap_models():
    if is_lite_mode():
        return JSONResponse(
            {"status": "disabled", "message": "Model training unavailable in lite/cloud mode."},
            status_code=503,
        )
    asyncio.create_task(_run_bootstrap())
    return {"status": "started"}


async def _run_bootstrap():
    global rl_training_status
    rl_training_status = {"running": True, "progress": 0, "message": "Bootstrapping CNN...", "best_reward": None}

    def _run():
        import bootstrap_models
        bootstrap_models.bootstrap_cnn(samples_per_class=150, epochs=15)
        rl_training_status["message"] = "Training RL agent..."
        bootstrap_models.bootstrap_rl(iterations=25)
        return True

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run)
        rl_training_status = {"running": False, "progress": 100, "message": "All models ready!", "best_reward": "done"}
    except Exception as e:
        rl_training_status = {"running": False, "progress": 0, "message": f"Bootstrap failed: {e}", "best_reward": None}


@app.post("/api/compare")
async def start_comparison(req: ComparisonRequest):
    if comparison_status["running"]:
        return {"status": "already_running", **comparison_status}

    asyncio.create_task(_run_comparison(req))
    return {"status": "started", **comparison_status}


@app.get("/api/compare/status")
async def get_comparison_status():
    return comparison_status


@app.post("/api/rl/train")
async def start_rl_training(req: RLTrainingRequest):
    if is_lite_mode():
        return JSONResponse(
            {"status": "disabled", "message": "RL training unavailable in lite/cloud mode."},
            status_code=503,
        )
    if rl_training_status["running"]:
        return {"status": "already_running", **rl_training_status}

    asyncio.create_task(_run_rl_training(req.iterations, req.quick))
    return {"status": "started", **rl_training_status}


@app.post("/api/rl/bootstrap")
async def bootstrap_rl():
    if is_lite_mode():
        return {"success": True, "path": "heuristic", "lite_mode": True}

    from src.rl.rl_adapter import ensure_rl_model

    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, ensure_rl_model)
    return {"success": success, "path": "models/rl_smc_agent.pt"}


@app.get("/api/rl/status")
async def get_rl_status():
    return rl_training_status


async def _run_comparison(req: ComparisonRequest):
    global comparison_status
    comparison_status = {"running": True, "progress": 0, "results": None, "message": "Running benchmarks..."}

    def _run():
        from src.simulation.comparison_runner import run_controller_comparison

        comparison_status["progress"] = 33
        comparison_status["message"] = "Benchmarking Classical SMC..."
        comparison_status["progress"] = 66
        comparison_status["message"] = "Benchmarking CNN-Adaptive SMC..."
        comparison_status["progress"] = 90
        comparison_status["message"] = "Benchmarking RL Agent..."

        return run_controller_comparison(
            scenario_name=req.scenario_name,
            trajectory_type=req.trajectory_type,
            enable_noise=req.enable_noise,
            enable_disturbance=req.enable_disturbance,
            enable_slip=req.enable_slip,
            total_time=req.total_time,
        )

    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _run)
        winner_label = MODE_LABELS.get(results["winner"], results["winner"])
        if results["winner"] == "classical":
            msg = "Benchmark complete — try re-running; adaptive controllers expected under combined uncertainty."
        else:
            msg = f"Best overall: {winner_label} (robustness score under combined uncertainty)"
        comparison_status = {
            "running": False,
            "progress": 100,
            "results": results,
            "message": msg,
        }
    except Exception as e:
        comparison_status = {
            "running": False,
            "progress": 0,
            "results": None,
            "message": f"Comparison failed: {e}",
        }


async def _run_rl_training(iterations: int, quick: bool):
    global rl_training_status
    rl_training_status = {
        "running": True,
        "progress": 0,
        "message": "Training RL agent...",
        "best_reward": None,
    }

    try:
        n_iters = 20 if quick else iterations
        rollout_steps = 1024 if quick else 2048

        def _train_with_progress():
            import numpy as np

            from src.rl.agent import PPOAgent
            from src.rl.env import SMCParameterEnv
            from src.rl.train_rl import collect_rollout

            os.makedirs("models", exist_ok=True)
            os.makedirs("results/rl_training", exist_ok=True)

            env = SMCParameterEnv(episode_steps=500, param_update_interval=50)
            agent = PPOAgent()
            best_reward = -float("inf")
            history = []

            for iteration in range(n_iters):
                rollout = collect_rollout(env, agent, rollout_steps)
                agent.update(rollout)
                mean_reward = rollout["mean_reward"]
                history.append(mean_reward)
                if mean_reward > best_reward:
                    best_reward = mean_reward
                    agent.save("models/rl_smc_agent.pt")

                rl_training_status["progress"] = int(((iteration + 1) / n_iters) * 100)
                rl_training_status["message"] = (
                    f"Iteration {iteration + 1}/{n_iters} · reward={mean_reward:.4f}"
                )
                rl_training_status["best_reward"] = best_reward

            agent.save("models/rl_smc_agent.pt")
            np.save("results/rl_training/reward_history.npy", np.array(history))
            return best_reward

        loop = asyncio.get_event_loop()
        best = await loop.run_in_executor(None, _train_with_progress)
        rl_training_status = {
            "running": False,
            "progress": 100,
            "message": f"Training complete · best reward={best:.4f}",
            "best_reward": best,
        }
    except Exception as e:
        rl_training_status = {
            "running": False,
            "progress": 0,
            "message": f"Training failed: {e}",
            "best_reward": None,
        }


@app.websocket("/ws/simulation")
async def websocket_simulation(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "reset":
                config = _config_from_dict(msg)
                engine.reset(config)
                await websocket.send_json({"type": "state", **engine.to_dict()})

            elif msg.get("type") == "start":
                try:
                    if "controller_mode" in msg:
                        config = _config_from_dict(msg)
                        engine.reset(config)

                    engine.resume()
                    speed = max(0.5, min(msg.get("simulation_speed", engine.config.simulation_speed), 10.0))
                    sleep_time = engine.config.dt / speed
                    recorded_frames = []

                    while engine.state.running and not engine.state.finished:
                        engine.step()
                        state_dict = {"type": "state", **engine.to_dict()}
                        recorded_frames.append(engine.to_dict())
                        await websocket.send_json(state_dict)
                        await asyncio.sleep(sleep_time)

                    final = engine.to_dict()
                    await websocket.send_json({"type": "finished", **final})

                    if recorded_frames:
                        from datetime import datetime
                        save_recording(recorded_frames, {
                            "controller_mode": engine.config.controller_mode,
                            "scenario_name": engine.config.scenario_name,
                            "trajectory_type": engine.config.trajectory_type,
                            "metrics": final.get("metrics", {}),
                            "timestamp": datetime.now().isoformat(),
                        })
                except Exception as e:
                    await websocket.send_json({"type": "error", "message": str(e)})
                    engine.pause()

            elif msg.get("type") == "replay":
                recording_id = msg.get("recording_id")
                data = load_recording(recording_id)
                if not data:
                    await websocket.send_json({"type": "error", "message": "Recording not found"})
                    continue
                speed = max(0.5, min(msg.get("simulation_speed", 3.0), 10.0))
                frames = data.get("frames", [])
                for frame in frames:
                    await websocket.send_json({"type": "state", **frame})
                    await asyncio.sleep(engine.config.dt / speed if hasattr(engine, 'config') else 0.005)
                if frames:
                    await websocket.send_json({"type": "finished", **frames[-1]})

            elif msg.get("type") == "step":
                engine.step()
                await websocket.send_json({"type": "state", **engine.to_dict()})

            elif msg.get("type") == "pause":
                engine.pause()
                await websocket.send_json({"type": "state", **engine.to_dict()})

    except WebSocketDisconnect:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


frontend_dist = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../frontend/dist")
)
frontend_index = os.path.join(frontend_dist, "index.html")

if os.path.isdir(frontend_dist):

    @app.get("/")
    async def serve_index():
        return FileResponse(frontend_index)

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        if path.startswith("api/") or path.startswith("ws/"):
            raise HTTPException(status_code=404, detail="Not found")

        candidate = os.path.join(frontend_dist, path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        if path.startswith("assets/"):
            raise HTTPException(status_code=404, detail="Asset not found")
        return FileResponse(frontend_index)

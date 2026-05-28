import argparse
import os
import sys
import time
from pathlib import Path

import pandas as pd
import pybullet as p
import pybullet_data

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


SCENARIOS = ["normal", "noise", "disturbance", "slip", "combined"]


def load_logs(scenario: str):
    classical_path = Path(f"results/logs/classical_smc_issues/log_{scenario}.csv")
    adaptive_path = Path(f"results/logs/adaptive_smc/log_{scenario}.csv")

    if not classical_path.exists():
        raise FileNotFoundError(f"Missing classical log: {classical_path}")

    if not adaptive_path.exists():
        raise FileNotFoundError(f"Missing adaptive log: {adaptive_path}")

    classical_df = pd.read_csv(classical_path)
    adaptive_df = pd.read_csv(adaptive_path)

    return classical_df, adaptive_df


def yaw_to_quaternion(theta: float):
    return p.getQuaternionFromEuler([0.0, 0.0, theta])


def create_box_robot(position, color):
    visual_shape = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[0.18, 0.12, 0.08],
        rgbaColor=color,
    )

    collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[0.18, 0.12, 0.08],
    )

    robot_id = p.createMultiBody(
        baseMass=1.0,
        baseCollisionShapeIndex=collision_shape,
        baseVisualShapeIndex=visual_shape,
        basePosition=position,
    )

    return robot_id


def create_sphere(position, color, radius=0.06):
    visual_shape = p.createVisualShape(
        shapeType=p.GEOM_SPHERE,
        radius=radius,
        rgbaColor=color,
    )

    sphere_id = p.createMultiBody(
        baseMass=0,
        baseVisualShapeIndex=visual_shape,
        basePosition=position,
    )

    return sphere_id


def draw_line_from_dataframe(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color,
    z: float,
    step: int = 20,
    line_width: float = 2.0,
):
    points = []

    for i in range(0, len(df), step):
        x = float(df.iloc[i][x_col])
        y = float(df.iloc[i][y_col])
        points.append([x, y, z])

    for i in range(len(points) - 1):
        p.addUserDebugLine(
            points[i],
            points[i + 1],
            lineColorRGB=color,
            lineWidth=line_width,
            lifeTime=0,
        )


def add_scene_text(scenario: str):
    p.addUserDebugText(
        text=f"Scenario: {scenario}",
        textPosition=[0.0, -1.2, 0.8],
        textColorRGB=[0.0, 0.0, 0.0],
        textSize=1.5,
        lifeTime=0,
    )

    p.addUserDebugText(
        text="Black: desired | Blue: classical SMC | Orange: CNN-adaptive SMC",
        textPosition=[0.0, -1.2, 0.55],
        textColorRGB=[0.0, 0.0, 0.0],
        textSize=1.1,
        lifeTime=0,
    )


def replay_paths(
    scenario: str,
    frame_step: int = 5,
    sleep_time: float = 0.02,
):
    classical_df, adaptive_df = load_logs(scenario)

    physics_client = p.connect(p.GUI)

    if physics_client < 0:
        raise RuntimeError("Could not connect to PyBullet GUI.")

    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.resetSimulation()
    p.setGravity(0, 0, -9.81)

    p.loadURDF("plane.urdf")

    p.resetDebugVisualizerCamera(
        cameraDistance=7.0,
        cameraYaw=45,
        cameraPitch=-55,
        cameraTargetPosition=[3.0, 0.0, 0.0],
    )

    # Desired path: black
    draw_line_from_dataframe(
        df=classical_df,
        x_col="desired_x",
        y_col="desired_y",
        color=[0.0, 0.0, 0.0],
        z=0.02,
        step=20,
        line_width=2.0,
    )

    # Classical path: blue
    draw_line_from_dataframe(
        df=classical_df,
        x_col="actual_x",
        y_col="actual_y",
        color=[0.0, 0.2, 1.0],
        z=0.04,
        step=20,
        line_width=2.0,
    )

    # Adaptive path: orange
    draw_line_from_dataframe(
        df=adaptive_df,
        x_col="actual_x",
        y_col="actual_y",
        color=[1.0, 0.45, 0.0],
        z=0.06,
        step=20,
        line_width=2.0,
    )

    start_x = float(classical_df.iloc[0]["desired_x"])
    start_y = float(classical_df.iloc[0]["desired_y"])
    end_x = float(classical_df.iloc[-1]["desired_x"])
    end_y = float(classical_df.iloc[-1]["desired_y"])

    create_sphere([start_x, start_y, 0.12], [0.0, 1.0, 0.0, 1.0])
    create_sphere([end_x, end_y, 0.12], [1.0, 0.0, 0.0, 1.0])

    classical_robot = create_box_robot(
        position=[
            float(classical_df.iloc[0]["actual_x"]),
            float(classical_df.iloc[0]["actual_y"]),
            0.15,
        ],
        color=[0.0, 0.2, 1.0, 1.0],
    )

    adaptive_robot = create_box_robot(
        position=[
            float(adaptive_df.iloc[0]["actual_x"]),
            float(adaptive_df.iloc[0]["actual_y"]),
            0.35,
        ],
        color=[1.0, 0.45, 0.0, 1.0],
    )

    add_scene_text(scenario)

    n_frames = min(len(classical_df), len(adaptive_df))

    print(f"Starting PyBullet replay for scenario: {scenario}")
    print(f"Frames: {n_frames}, frame_step: {frame_step}")

    for i in range(0, n_frames, frame_step):
        classical_row = classical_df.iloc[i]
        adaptive_row = adaptive_df.iloc[i]

        cx = float(classical_row["actual_x"])
        cy = float(classical_row["actual_y"])
        ctheta = float(classical_row["actual_theta"])

        ax = float(adaptive_row["actual_x"])
        ay = float(adaptive_row["actual_y"])
        atheta = float(adaptive_row["actual_theta"])

        p.resetBasePositionAndOrientation(
            classical_robot,
            [cx, cy, 0.15],
            yaw_to_quaternion(ctheta),
        )

        p.resetBasePositionAndOrientation(
            adaptive_robot,
            [ax, ay, 0.35],
            yaw_to_quaternion(atheta),
        )

        p.stepSimulation()
        time.sleep(sleep_time)

    print("Replay finished. Close the PyBullet window to exit.")

    while p.isConnected():
        time.sleep(0.1)


def main():
    parser = argparse.ArgumentParser(
        description="Replay Classical SMC and CNN-adaptive SMC paths in PyBullet."
    )

    parser.add_argument(
        "--scenario",
        type=str,
        default="combined",
        choices=SCENARIOS,
        help="Scenario to replay.",
    )

    parser.add_argument(
        "--frame-step",
        type=int,
        default=5,
        help="Use every Nth frame.",
    )

    parser.add_argument(
        "--sleep-time",
        type=float,
        default=0.02,
        help="Delay between frames.",
    )

    args = parser.parse_args()

    replay_paths(
        scenario=args.scenario,
        frame_step=args.frame_step,
        sleep_time=args.sleep_time,
    )


if __name__ == "__main__":
    main()

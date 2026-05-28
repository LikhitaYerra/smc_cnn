import os
import sys
from textwrap import fill
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.image import imread

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


OUTPUT_PATH = Path("results/reports/project_report.pdf")

PAGES = [
    {
        "type": "text",
        "title": "CNN-Adaptive Sliding Mode Control",
        "subtitle": "Autonomous Robot Project Report",
        "body": [
            "Overview",
            "This project compares classical Sliding Mode Control (SMC) with",
            "CNN-adaptive SMC for a differential-drive mobile robot.",
            "",
            "Problem",
            "Fixed SMC parameters cannot perform well under noise, disturbance,",
            "and wheel slip at the same time.",
            "",
            "Approach",
            "A CNN reads a 64×64 environment map, predicts the scenario",
            "(normal, noise, disturbance, slip, combined), and selects",
            "appropriate SMC gains for that condition.",
            "",
            "Goal",
            "Improve tracking and reduce control chattering under uncertainty.",
        ],
    },
    {
        "type": "text",
        "title": "Method & Simulation Setup",
        "body": [
            "Pipeline",
            "1. Generate synthetic CNN maps (1500 samples, 5 classes)",
            "2. Train CNN classifier (3 conv blocks + FC layer)",
            "3. Simulate classical vs adaptive SMC in 5 scenarios",
            "4. Compare tracking error, chattering, and control effort",
            "",
            "Robot & trajectory",
            "Differential-drive robot, straight path at 0.3 m/s for 20 s.",
            "Start pose: (0, 0.5). Legend: blue = classical, orange = adaptive.",
            "",
            "Scenarios",
            "Normal | Noise | Disturbance (push at t=8s) | Slip (t=10–14s) | Combined",
        ],
    },
    {
        "type": "image",
        "title": "Simulation Environments",
        "caption": "Five CNN input maps representing different operating conditions.",
        "path": "results/snapshots/simulation/simulation_environment_overview.png",
    },
    {
        "type": "image",
        "title": "Combined Scenario",
        "caption": "Hardest test case with noise, disturbance, and slip active together.",
        "path": "results/snapshots/simulation/combined_environment.png",
    },
    {
        "type": "image",
        "title": "Disturbance Recovery",
        "caption": "Robot response at t = 0, 8, 12, and 20 s after an external push at t = 8 s.",
        "path": "results/snapshots/simulation/disturbance_keyframes.png",
    },
    {
        "type": "image",
        "title": "3D Path Replay",
        "caption": "3D visualization of classical (blue) and adaptive (orange) robot paths.",
        "path": "results/snapshots/3d_simulation/combined_3d_environment.png",
    },
    {
        "type": "text",
        "title": "CNN Classifier",
        "body": [
            "Input: 64×64 grayscale map  |  Output: 5 scenario classes",
            "",
            "Test accuracy: 100% on synthetic data.",
            "",
            "Note: High accuracy is expected because each class uses distinct",
            "visual markers. Real sensor maps would be more challenging.",
        ],
    },
    {
        "type": "image",
        "title": "CNN Test Results",
        "caption": "Confusion matrix on the held-out test set.",
        "path": "results/plots/cnn/cnn_test_confusion_matrix.png",
    },
    {
        "type": "image",
        "title": "Trajectory Comparison",
        "caption": "Classical vs CNN-adaptive SMC across all five scenarios.",
        "path": "results/plots/summary/trajectory_grid.png",
    },
    {
        "type": "image",
        "title": "Results Heatmap",
        "caption": "Adaptive improvement over classical SMC (%). Green = adaptive better.",
        "path": "results/plots/summary/improvement_heatmap.png",
    },
    {
        "type": "text",
        "title": "Results & Conclusion",
        "body": [
            "Key results (adaptive vs classical)",
            "Noise:        chattering  +35.5%   (smoother control)",
            "Disturbance:  final error +37.0%   (better recovery)",
            "Slip:         final error +32.3%   (better recovery)",
            "Combined:     chattering  +27.7%",
            "",
            "Trade-off: smoother control in noise can reduce tracking precision.",
            "",
            "Conclusion",
            "CNN-adaptive SMC adapts gains to detected conditions and improves",
            "recovery and smoothness where fixed parameters are insufficient.",
            "",
            "Future work",
            "Other sim environments (PyBullet, Gazebo, ROS), reinforcement learning",
            "for prediction, and physical robot deployment.",
        ],
    },
]


def draw_text_page(fig, page: dict):
    fig.patch.set_facecolor("white")

    title = page.get("title", "")
    subtitle = page.get("subtitle", "")
    body = page.get("body", [])

    fig.text(0.5, 0.92, title, ha="center", va="top", fontsize=18, fontweight="bold")

    if subtitle:
        fig.text(0.5, 0.86, subtitle, ha="center", va="top", fontsize=12, color="#444444")

    y = 0.80 if subtitle else 0.88
    section_headers = {
        "Overview", "Problem", "Approach", "Comparison", "Objective",
        "Sliding Mode Control (SMC)", "CNN Environment Classifier",
        "Adaptive Parameter Selection", "Robot model", "Reference trajectory",
        "Test scenarios", "Legend (figures)", "Implementation:",
        "Input:", "Output:", "Architecture:", "Dataset:", "Test accuracy:",
        "Note:", "Strengths", "Limitations", "Conclusion", "Future work",
    }

    for line in body:
        if line in section_headers or line.endswith(":") and len(line) < 40:
            fig.text(0.10, y, line, ha="left", va="top", fontsize=11, fontweight="bold")
        elif line.startswith("Scenario") or line.startswith("Normal:") or line.startswith("Noise:"):
            fig.text(0.10, y, line, ha="left", va="top", fontsize=10, family="monospace")
        else:
            fig.text(0.10, y, line, ha="left", va="top", fontsize=10.5)
        y -= 0.032

        if y < 0.05:
            break


def draw_image_page(fig, page: dict):
    image_path = Path(page["path"])
    if not image_path.exists():
        draw_text_page(
            fig,
            {
                "title": page["title"],
                "body": [f"Missing image: {image_path}"],
            },
        )
        return

    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.965, page["title"], ha="center", va="top", fontsize=15, fontweight="bold")

    img = imread(image_path)
    ax = fig.add_axes([0.06, 0.16, 0.88, 0.74])
    ax.imshow(img)
    ax.axis("off")

    fig.text(
        0.5,
        0.06,
        fill(page.get("caption", ""), width=100),
        ha="center",
        va="bottom",
        fontsize=10,
        color="#333333",
    )


def generate_pdf():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    snapshot_dir = Path("results/snapshots/simulation")
    if not snapshot_dir.exists() or not any(snapshot_dir.glob("*.png")):
        from src.visualization.capture_simulation_snapshots import capture_all_snapshots

        print("Generating 2D simulation snapshots first...")
        capture_all_snapshots()

    snapshot_3d_dir = Path("results/snapshots/3d_simulation")
    if not snapshot_3d_dir.exists() or not any(snapshot_3d_dir.glob("*.png")):
        from src.visualization.capture_3d_snapshots import capture_all_3d_snapshots

        print("Generating 3D simulation snapshots first...")
        capture_all_3d_snapshots()

    with PdfPages(OUTPUT_PATH) as pdf:
        for index, page in enumerate(PAGES, start=1):
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(0.95, 0.02, f"{index}", ha="right", va="bottom", fontsize=9, color="#888888")

            if page["type"] == "text":
                draw_text_page(fig, page)
            else:
                draw_image_page(fig, page)

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        d = pdf.infodict()
        d["Title"] = "CNN-Adaptive SMC Project Report"
        d["Author"] = "AI-SMC Autonomous Robot Project"
        d["Subject"] = "CNN-adaptive sliding mode control for autonomous robots"

    print(f"PDF report saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_pdf()

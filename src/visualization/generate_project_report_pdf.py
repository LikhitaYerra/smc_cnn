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
            "This project implements and evaluates a CNN-adaptive Sliding Mode",
            "Controller for a differential-drive autonomous mobile robot.",
            "",
            "Problem",
            "Fixed control parameters cannot perform optimally under all",
            "conditions such as sensor noise, external disturbances, and",
            "wheel slip.",
            "",
            "Approach",
            "A CNN classifies the operating scenario from a 64×64 environment",
            "map and selects appropriate SMC parameters for that condition.",
            "",
            "Comparison",
            "Classical SMC (fixed gains) vs CNN-adaptive SMC (scenario-based gains)",
            "",
            "Objective",
            "Improve path tracking and reduce control chattering under uncertainty.",
        ],
    },
    {
        "type": "text",
        "title": "Background",
        "body": [
            "Sliding Mode Control (SMC)",
            "SMC is a robust nonlinear control method that drives tracking error",
            "toward zero. It handles disturbances well but can produce chattering",
            "(rapid control oscillations) near the sliding surface.",
            "",
            "CNN Environment Classifier",
            "A convolutional neural network reads a grayscale environment map",
            "and predicts one of five scenarios: normal, noise, disturbance,",
            "slip, or combined.",
            "",
            "Adaptive Parameter Selection",
            "Each predicted scenario maps to a pre-tuned set of SMC gains.",
            "Smoother parameters are used under noise; stronger correction is",
            "used under disturbance and slip.",
        ],
    },
    {
        "type": "text",
        "title": "Methodology",
        "body": [
            "1. Robot simulation",
            "   Differential-drive kinematic model on a straight reference path.",
            "",
            "2. Dataset generation",
            "   1500 synthetic 64×64 maps (300 per scenario class).",
            "",
            "3. CNN training",
            "   Three-layer CNN with batch normalization and dropout.",
            "",
            "4. Controller evaluation",
            "   Classical, fuzzy, CNN-adaptive, oracle, and RL-adaptive SMC",
            "   tested under five scenarios.",
            "",
            "5. Performance metrics",
            "   Tracking error, control effort, chattering, and settling time.",
            "",
            "6. Visualization",
            "   2D plots, 3D path replay, and comparative analysis.",
        ],
    },
    {
        "type": "text",
        "title": "Simulation Environment",
        "body": [
            "Robot model",
            "• Differential-drive mobile robot (x, y, θ)",
            "• Initial pose: (0, 0.5), orientation θ = 0",
            "",
            "Reference trajectory",
            "• Straight line, speed 0.3 m/s, duration 20 s, dt = 0.01 s",
            "",
            "Test scenarios",
            "• Normal — no uncertainty",
            "• Noise — Gaussian sensor noise on position and orientation",
            "• Disturbance — external push (+0.4 m, y) at t = 8 s",
            "• Slip — 70% velocity effectiveness from t = 10–14 s",
            "• Combined — all effects applied together",
            "",
            "Legend (figures)",
            "Desired path: dashed black | Classical SMC: blue | CNN-adaptive: orange",
        ],
    },
    {
        "type": "image",
        "title": "Simulation Overview",
        "caption": "CNN environment maps for all five scenarios. Each class uses distinct visual features representing different operating conditions.",
        "path": "results/snapshots/simulation/simulation_environment_overview.png",
    },
    {
        "type": "image",
        "title": "Normal Scenario",
        "caption": "Baseline case with no uncertainty. Both controllers use identical parameters, serving as a validation reference.",
        "path": "results/snapshots/simulation/normal_environment.png",
    },
    {
        "type": "image",
        "title": "Noise Scenario",
        "caption": "Sensor noise applied to state measurements. Adaptive SMC selects smoother gains to reduce control chattering.",
        "path": "results/snapshots/simulation/noise_environment.png",
    },
    {
        "type": "image",
        "title": "Noise — Keyframes",
        "caption": "Robot positions at t = 0, 8, 12, and 20 s. Classical SMC (blue) and CNN-adaptive SMC (orange).",
        "path": "results/snapshots/simulation/noise_keyframes.png",
    },
    {
        "type": "image",
        "title": "Disturbance Scenario",
        "caption": "External disturbance applied at t = 8 s. Adaptive SMC uses stronger correction gains for faster recovery.",
        "path": "results/snapshots/simulation/disturbance_environment.png",
    },
    {
        "type": "image",
        "title": "Disturbance — Keyframes",
        "caption": "Disturbance occurs at x ≈ 2.4 m. Both controllers recover; adaptive SMC shows improved final tracking error.",
        "path": "results/snapshots/simulation/disturbance_keyframes.png",
    },
    {
        "type": "image",
        "title": "Slip Scenario",
        "caption": "Wheel slip reduces effective velocity by 30% during t = 10–14 s. Adaptive gains compensate for reduced traction.",
        "path": "results/snapshots/simulation/slip_environment.png",
    },
    {
        "type": "image",
        "title": "Combined Scenario",
        "caption": "All uncertainty effects active simultaneously — the most challenging test condition.",
        "path": "results/snapshots/simulation/combined_environment.png",
    },
    {
        "type": "image",
        "title": "Combined — Keyframes",
        "caption": "Combined scenario at four time steps. Adaptive SMC maintains smoother control while recovering from disturbance.",
        "path": "results/snapshots/simulation/combined_keyframes.png",
    },
    {
        "type": "text",
        "title": "3D Visualization",
        "body": [
            "A PyBullet-based 3D module replays saved simulation logs on a",
            "ground plane with two robot models and colored path trails.",
            "",
            "Implementation: src/pybullet_sim/replay_controller_paths.py",
            "",
            "The 3D environment is used for visualization only. Controller",
            "evaluation is performed in the 2D kinematic simulation. The 3D",
            "views below are rendered from the same logged trajectory data.",
        ],
    },
    {
        "type": "image",
        "title": "3D View — Combined Scenario",
        "caption": "3D path replay of the combined scenario. Blue: classical SMC. Orange: CNN-adaptive SMC. Black dashed: desired path.",
        "path": "results/snapshots/3d_simulation/combined_3d_environment.png",
    },
    {
        "type": "image",
        "title": "3D Keyframes — Disturbance",
        "caption": "3D views at t = 0, 8, 12, and 20 s showing disturbance response and path recovery.",
        "path": "results/snapshots/3d_simulation/disturbance_3d_keyframes.png",
    },
    {
        "type": "image",
        "title": "3D View — Noise Scenario",
        "caption": "3D path comparison under sensor noise. Adaptive SMC produces a smoother trajectory.",
        "path": "results/snapshots/3d_simulation/noise_3d_environment.png",
    },
    {
        "type": "text",
        "title": "Extended Experiments",
        "body": [
            "Beyond classical vs CNN-adaptive SMC, four additional experiments",
            "were implemented to strengthen the DELCON 2026 submission:",
            "",
            "Fuzzy-SMC baseline",
            "Mamdani-style fuzzy rules map tracking error and chattering proxy",
            "to SMC gain adjustments (φ, kω, λy, smoothing).",
            "",
            "Oracle adaptive SMC",
            "Uses the true scenario label (perfect classification) as an",
            "upper-bound reference for CNN-driven gain scheduling.",
            "",
            "RL-adaptive SMC",
            "PPO policy (80k steps, Gymnasium env) selects among five SMC",
            "parameter presets from online error/chattering observations.",
            "",
            "Realistic occupancy maps",
            "Second CNN dataset with walls, clutter, and subtler class cues;",
            "test accuracy drops to 95.1% (credible vs 100% on simple maps).",
        ],
    },
    {
        "type": "text",
        "title": "CNN Classifier",
        "body": [
            "Input: 1 × 64 × 64 grayscale map",
            "Output: 5-class scenario label",
            "",
            "Architecture: 3 convolution blocks, batch norm, max pooling,",
            "fully connected layer with dropout (p = 0.3). ~534k parameters.",
            "",
            "Simple-map dataset: 1050 train / 225 val / 225 test.",
            "Test accuracy: 100% (engineered separability; RF baseline also 100%).",
            "",
            "Realistic-map dataset: walls + corridor clutter.",
            "Test accuracy: 95.1% (k-NN 41.3%, logistic regression 72.9%).",
            "",
            "Interpretation: perfect simple-map scores are expected by design;",
            "the realistic benchmark provides reviewer-credible generalisation.",
        ],
    },
    {
        "type": "image",
        "title": "CNN Training Data (Simple Maps)",
        "caption": "Simple synthetic environment maps for each scenario class. CNN test accuracy: 100%.",
        "path": "results/plots/cnn_dataset/dataset_preview.png",
    },
    {
        "type": "image",
        "title": "Realistic CNN Training Data",
        "caption": "Realistic occupancy maps with random walls and corridor clutter. CNN test accuracy on this split: 95.1%.",
        "path": "results/plots/cnn_dataset_realistic/realistic_dataset_preview.png",
    },
    {
        "type": "image",
        "title": "CNN Test Results",
        "caption": "Confusion matrix on the held-out test set. All five classes classified correctly.",
        "path": "results/plots/cnn/cnn_test_confusion_matrix.png",
    },
    {
        "type": "text",
        "title": "Evaluation Metrics",
        "body": [
            "Tracking error — distance from robot to desired path",
            "RMSE tracking error — root mean square error over the simulation",
            "Final tracking error — error at t = 20 s",
            "Control effort — cumulative control command intensity",
            "Chattering index — sum of angular velocity changes (lower = smoother)",
            "Settling time — time for error to remain below threshold",
            "",
            "Improvement (%) — positive values indicate adaptive SMC outperforms",
            "classical SMC on that metric.",
        ],
    },
    {
        "type": "image",
        "title": "Trajectory Comparison",
        "caption": "Classical vs CNN-adaptive SMC paths across all five scenarios.",
        "path": "results/plots/summary/trajectory_grid.png",
    },
    {
        "type": "image",
        "title": "Tracking Error",
        "caption": "Tracking error over time for each scenario. Spikes correspond to disturbance and slip events.",
        "path": "results/plots/summary/tracking_error_grid.png",
    },
    {
        "type": "image",
        "title": "Chattering Comparison",
        "caption": "Chattering index comparison. Adaptive SMC reduces oscillations in noise and combined scenarios.",
        "path": "results/plots/summary/chattering_comparison.png",
    },
    {
        "type": "text",
        "title": "Multi-Controller Comparison",
        "body": [
            "All five controllers evaluated on identical simulation conditions.",
            "",
            "Chattering index (noise scenario)",
            "  Classical: 76.5  |  Fuzzy: 70.5  |  CNN: 49.1",
            "  Oracle: 49.3  |  RL: 50.7",
            "",
            "Final tracking error — disturbance (mm)",
            "  Classical: 20.9  |  Fuzzy: 24.8  |  CNN: 17.9",
            "  Oracle: 15.6  |  RL: 32.8",
            "",
            "Final tracking error — slip (mm)",
            "  Classical: 40.7  |  Fuzzy: 30.4  |  CNN: 27.4",
            "  Oracle: 27.4  |  RL: 41.6",
            "",
            "Key findings",
            "• CNN-adaptive matches oracle on noise chattering (near-optimal)",
            "• Oracle establishes ceiling: 15.6 mm vs CNN 17.9 mm (disturbance)",
            "• Fuzzy-SMC helps on slip but is inconsistent on disturbance",
            "• RL wins combined chattering (48.9) but needs more training elsewhere",
        ],
    },
    {
        "type": "image",
        "title": "Multi-Controller Chattering",
        "caption": "Chattering index across all five controllers and scenarios. CNN-adaptive achieves largest reductions under noise and combined uncertainty.",
        "path": "results/plots/multi_controller/chattering_all_controllers.png",
    },
    {
        "type": "image",
        "title": "Multi-Controller Final Error",
        "caption": "Final tracking error at t = 20 s. CNN-adaptive and oracle outperform classical and fuzzy under disturbance and slip.",
        "path": "results/plots/multi_controller/final_error_all_controllers.png",
    },
    {
        "type": "image",
        "title": "Multi-Controller RMSE",
        "caption": "RMSE tracking error comparison across all adaptive baselines.",
        "path": "results/plots/multi_controller/rmse_all_controllers.png",
    },
    {
        "type": "text",
        "title": "CNN vs Classical — Results Summary",
        "body": [
            "Scenario          Chattering    Final Error",
            "Normal                 0%              0%",
            "Noise               +35.5%          -15.0%",
            "Disturbance         -12.2%          +37.0%",
            "Slip                -22.5%          +32.3%",
            "Combined            +27.7%           +2.2%",
            "",
            "Normal: No improvement expected — both controllers use the same gains.",
            "",
            "Noise: Adaptive SMC reduces chattering by 35.5% with a trade-off in",
            "tracking accuracy (RMSE increases by ~11%).",
            "",
            "Disturbance: Final tracking error improves by 37.0%, demonstrating",
            "better recovery after external push.",
            "",
            "Slip: Final tracking error improves by 32.3% under reduced traction.",
            "",
            "Combined: Chattering reduced by 27.7%; mixed results on other metrics.",
        ],
    },
    {
        "type": "image",
        "title": "Improvement Heatmap",
        "caption": "Percentage improvement of adaptive SMC over classical SMC. Green: adaptive better. Red: classical better.",
        "path": "results/plots/summary/improvement_heatmap.png",
    },
    {
        "type": "text",
        "title": "Discussion",
        "body": [
            "The CNN-adaptive approach demonstrates scenario-dependent performance.",
            "It does not improve every metric uniformly.",
            "",
            "Strengths",
            "• Significant chattering reduction in noisy conditions (~36%)",
            "• Improved recovery after disturbance and slip (~33–37%)",
            "• Near-oracle performance when CNN classification is correct",
            "• Realistic-map CNN reaches 95.1% (reviewer-credible benchmark)",
            "",
            "Limitations",
            "• Simple-map CNN accuracy is 100% by engineered design",
            "• Tracking accuracy trade-off in noisy conditions",
            "• RL and fuzzy baselines need further tuning for all scenarios",
            "",
            "Overall, adaptive SMC is most beneficial when operating conditions",
            "deviate from the ideal normal case.",
        ],
    },
    {
        "type": "text",
        "title": "DELCON 2026 Submission",
        "body": [
            "Conference: IEEE DELCON 2026, BITS Pilani, India",
            "Deadline: 15 July 2026 (EDAS submission)",
            "Format: 6-page IEEE two-column, double-blind review",
            "",
            "Paper files",
            "• delcon2026_paper.tex / delcon2026_paper.pdf",
            "• delcon2026_latex.zip (LaTeX source + figures)",
            "",
            "Submission checklist",
            "• Anonymous PDF (no author names in manuscript)",
            "• All 7 authors entered in EDAS only",
            "• CNN 100% accuracy justified with baseline + realistic maps",
            "• Multi-controller comparison (fuzzy, oracle, RL) included",
            "• Accepted papers published in IEEE Xplore",
            "",
            "Repository: github.com/LikhitaYerra/smc_cnn",
        ],
    },
    {
        "type": "text",
        "title": "Conclusion & Future Work",
        "body": [
            "Conclusion",
            "This project delivers a CNN-guided adaptive SMC pipeline: the network",
            "classifies which operating problem the robot faces (normal, noise,",
            "disturbance, slip, combined), and the controller switches to a",
            "corresponding SMC mode with predefined parameters. Results show",
            "scenario-dependent gains versus classical fixed-gain SMC.",
            "",
            "Current approach (clarification)",
            "• CNN provides intelligent classification of the environment condition",
            "• Each class maps to a hand-tuned parameter set (smoother vs stronger mode)",
            "• The CNN does not yet predict λ, φ, α, k_v, k_ω directly from sensors",
            "",
            "Near-term extensions",
            "• Train CNN (or regressor head) to output SMC hyperparameters continuously",
            "• Grade uncertainty finely (e.g. light vs severe slip) — not one preset",
            "• Richer simulation: ROS / Gazebo / PyBullet with LiDAR-style maps",
            "• Natural uncertainty in the scene (not only injected faults)",
            "• Classifier detects operating condition in situ",
            "• Validate on university diff-drive robot (additional hardware track)",
            "",
            "Advanced research (publication extension)",
            "• RL policy training with larger scenario randomisation",
            "• Real LiDAR/camera occupancy grids for CNN input",
            "• Physical diff-drive robot validation at university lab",
            "• Hybrid LLM + CNN agent for scenario-aware control (latency study)",
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
        "Note:", "Strengths", "Limitations", "Conclusion",
        "Current approach (clarification)", "Near-term extensions",
        "Advanced research (publication extension)", "Key findings",
        "Chattering index (noise scenario)", "Final tracking error",
        "Repository:", "Conference:", "Paper files", "Submission checklist",
    }

    line_height = 0.028

    for line in body:
        if line in section_headers or (line.endswith(":") and len(line) < 40):
            fig.text(0.10, y, line, ha="left", va="top", fontsize=11, fontweight="bold")
            y -= line_height
        elif line.startswith("Scenario") or line.startswith("Normal:") or line.startswith("Noise:"):
            fig.text(0.10, y, line, ha="left", va="top", fontsize=10, family="monospace")
            y -= line_height
        else:
            wrapped_lines = fill(line, width=88).split("\n") if len(line) > 72 else [line]
            for subline in wrapped_lines:
                if y < 0.05:
                    break
                fig.text(0.10, y, subline, ha="left", va="top", fontsize=10.5)
                y -= line_height

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

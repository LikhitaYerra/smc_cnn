#!/usr/bin/env python3
"""Generate the AI Clinic research report PDF for defense submission."""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = ROOT / "docs" / "assets" / "aivancity_logo.png"
FIG_DIR = ROOT / "docs" / "assets" / "figures"
OUTPUT_PATH = ROOT / "docs" / "AI_Clinic_Research_Report.pdf"

# ── Edit these fields before final submission ──
REPORT_TITLE = (
    "CNN-Adaptive Sliding Mode Control and Reinforcement Learning "
    "for Autonomous Mobile Robot Navigation: A Digital Twin Approach"
)
STUDENT_NAMES = [
    "Likhit Ayerra",
    # Add co-authors below if applicable:
    # "Student Name 2",
]
SUPERVISOR_NAME = "[Supervisor Name — please update before submission]"
SUBMISSION_DATE = date(2026, 8, 28).strftime("%d %B %Y")
PROGRAM = "PGE5 — AI Clinic"


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
            spaceAfter=8,
        ),
        "heading1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            spaceBefore=16,
            spaceAfter=10,
            textColor=colors.HexColor("#0b3d5c"),
        ),
        "heading2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor("#145374"),
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            leftIndent=18,
            bulletIndent=6,
            spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
            spaceAfter=10,
        ),
    }
    return styles


def add_figure(story, styles, filename: str, caption: str, width: float = 15.5, aspect: float = 0.52):
    """Insert a centred figure with caption if the file exists."""
    path = FIG_DIR / filename
    if not path.exists():
        return
    img = Image(str(path), width=width * cm, height=width * cm * aspect)
    img.hAlign = "CENTER"
    story.append(Spacer(1, 0.15 * cm))
    story.append(img)
    story.append(Paragraph(caption, styles["caption"]))


def ensure_figures():
    """Generate report figures if missing."""
    required = [
        "fig01_architecture.png",
        "fig02_cnn_samples.png",
        "fig03_trajectory_comparison.png",
        "fig04_tracking_error.png",
        "fig05_rmse_bars.png",
        "fig06_chattering_bars.png",
        "fig07_controller_benchmark.png",
        "fig08_digital_twin.png",
    ]
    if not all((FIG_DIR / f).exists() for f in required):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "generate_report_figures",
            ROOT / "scripts" / "generate_report_figures.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.generate_all()


def title_page(story, styles):
    if LOGO_PATH.exists():
        logo = Image(str(LOGO_PATH), width=6 * cm, height=3.25 * cm)
        logo.hAlign = "CENTER"
        story.append(Spacer(1, 1.5 * cm))
        story.append(logo)
    else:
        story.append(Spacer(1, 3 * cm))
        story.append(Paragraph("aivancity", styles["title"]))

    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(REPORT_TITLE, styles["title"]))
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(PROGRAM, styles["subtitle"]))
    story.append(Spacer(1, 2 * cm))

    students = "<br/>".join(STUDENT_NAMES)
    meta_rows = [
        ["Participating Students", students],
        ["Supervisor", SUPERVISOR_NAME],
        ["Date of Submission", SUBMISSION_DATE],
    ]
    meta = Table(meta_rows, colWidths=[5.5 * cm, 10 * cm])
    meta.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(meta)
    add_figure(
        story, styles, "fig08_digital_twin.png",
        "Figure 0 — 3D Digital Twin interface for live robot simulation and controller comparison.",
        width=14, aspect=0.55,
    )
    story.append(PageBreak())


def section_intro(story, styles):
    story.append(Paragraph("1. Introduction", styles["heading1"]))

    story.append(Paragraph("1.1 Problem Statement", styles["heading2"]))
    story.append(
        Paragraph(
            "Autonomous mobile robots operating in real-world environments must follow desired "
            "trajectories accurately despite sensor noise, external disturbances, and actuator "
            "uncertainties such as wheel slip. Sliding Mode Control (SMC) is widely used for "
            "robust trajectory tracking because it provides strong rejection of matched "
            "disturbances. However, classical SMC relies on fixed controller gains tuned for "
            "a nominal operating condition. When the environment changes — for example when "
            "sensors become noisy, a push is applied to the robot, or wheels lose traction — "
            "fixed gains produce suboptimal performance: excessive chattering in noisy conditions, "
            "slow recovery after disturbances, or poor tracking under slip.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "This project addresses the following research question: <i>Can a learning-based "
            "perception and control pipeline improve the adaptability of sliding mode control "
            "for a differential-drive mobile robot under heterogeneous uncertainty conditions?</i> "
            "We propose and evaluate two complementary approaches: (1) a CNN-adaptive SMC "
            "framework that classifies the operating scenario from synthetic environment maps "
            "and switches SMC parameters accordingly, and (2) a Proximal Policy Optimization "
            "(PPO) reinforcement learning agent that learns continuous SMC gain adaptation from "
            "a reward signal balancing tracking accuracy, control effort, and chattering. Both "
            "approaches are integrated into a real-time 3D digital twin for visualization, "
            "comparison, and demonstration.",
            styles["body"],
        )
    )

    story.append(Paragraph("1.2 Literature Review", styles["heading2"]))
    story.append(
        Paragraph(
            "<b>Sliding Mode Control.</b> Sliding mode control, introduced by Utkin and further "
            "developed for robotic systems, enforces convergence to a sliding surface despite "
            "model uncertainty. For mobile robots, SMC has been applied to trajectory tracking "
            "of differential-drive platforms. A known limitation is chattering caused by "
            "discontinuous switching; boundary-layer and smoothing techniques are commonly used "
            "to mitigate this effect while preserving robustness.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Adaptive and Intelligent Control.</b> Adaptive SMC extends classical formulations "
            "by updating gains online based on estimated uncertainty. Recent work combines "
            "data-driven perception with control adaptation: convolutional neural networks have "
            "been used to interpret occupancy grids, LiDAR scans, or camera images for "
            "navigation and situation awareness. Mapping sensed context to controller parameters "
            "provides a practical middle ground between fully fixed controllers and fully "
            "learned end-to-end policies.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Deep Reinforcement Learning for Control.</b> Policy gradient methods, particularly "
            "PPO (Schulman et al., 2017), have shown success in continuous control tasks. "
            "In robotics, RL has been applied to tune low-level controllers, adapt gains, and "
            "handle domain randomization. Gymnasium-style environments enable repeatable "
            "training with measurable reward functions. For SMC, RL offers continuous parameter "
            "adaptation beyond discrete lookup tables, potentially improving performance in "
            "combined uncertainty scenarios.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Digital Twins.</b> Digital twin technology provides a virtual replica of a "
            "physical system for monitoring, simulation, and decision support. In healthcare "
            "and facility management, 3D twins visualize assets and agent behavior in context. "
            "For robotics research, a web-based 3D twin enables live demonstration of control "
            "algorithms, side-by-side controller comparison, and stakeholder communication during "
            "project defense.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Research Gap.</b> While SMC, CNN-based perception, and RL-based control have "
            "each been studied independently, few student-scale projects integrate all three "
            "within a unified simulation and visualization platform. This work fills that gap "
            "by implementing classical SMC, CNN-adaptive SMC, and PPO-adaptive SMC on the same "
            "robot model and evaluating them under identical scenarios.",
            styles["body"],
        )
    )
    add_figure(
        story, styles, "fig01_architecture.png",
        "Figure 1 — System architecture showing the CNN-adaptive SMC pipeline and PPO RL alternative.",
    )


def section_methodology(story, styles):
    story.append(Paragraph("2. Methodology", styles["heading1"]))

    story.append(Paragraph("2.1 Robot and Simulation Model", styles["heading2"]))
    story.append(
        Paragraph(
            "We model a differential-drive mobile robot with state "
            "(x, y, θ, v, ω). Kinematic integration uses Δt = 0.01 s. Desired trajectories "
            "include straight, circular, and S-curve paths. Uncertainty is injected through "
            "three mechanisms: Gaussian sensor noise on pose measurements, impulsive external "
            "disturbances, and multiplicative wheel slip reducing effective velocity.",
            styles["body"],
        )
    )

    story.append(Paragraph("2.2 Controllers", styles["heading2"]))
    bullets = [
        "<b>Classical SMC:</b> Fixed sliding surface gains (λ_x, λ_y, λ_θ), velocity gains "
        "(k_v, k_ω), boundary layer φ, and angular smoothing ω_smoothing.",
        "<b>CNN-Adaptive SMC:</b> A convolutional neural network classifies the scenario into "
        "five classes (normal, noise, disturbance, slip, combined) from 64×64 grayscale "
        "environment maps. Predicted class maps to a pre-defined SMC parameter set via lookup table.",
        "<b>RL Agent (PPO):</b> A continuous policy outputs normalized SMC parameters. The "
        "reward function penalizes tracking error, control effort, and chattering: "
        "r = −α·e² − β·(v² + ω²) − γ·|Δω|.",
    ]
    for item in bullets:
        story.append(Paragraph(f"• {item}", styles["bullet"]))

    story.append(Paragraph("2.3 CNN Training Pipeline", styles["heading2"]))
    story.append(
        Paragraph(
            "Synthetic environment maps were generated for each scenario class (600 samples total, "
            "120 per class). The dataset was split 70/15/15 into train/validation/test sets. "
            "The CNN architecture comprises three convolutional blocks (16→32→64 filters) with "
            "batch normalization, ReLU, max pooling, and a two-layer classifier with dropout. "
            "Training used Adam optimizer (lr = 0.001) and cross-entropy loss.",
            styles["body"],
        )
    )

    story.append(Paragraph("2.4 RL Training Pipeline", styles["heading2"]))
    story.append(
        Paragraph(
            "A Gymnasium environment wraps the SMC simulation with domain randomization across "
            "scenarios. The PPO agent uses an actor-critic architecture with Generalized Advantage "
            "Estimation (GAE). Training was performed for 20 iterations with 1024 rollout steps "
            "per iteration. The best policy checkpoint was saved based on mean episodic reward.",
            styles["body"],
        )
    )

    story.append(Paragraph("2.5 Evaluation Protocol", styles["heading2"]))
    story.append(
        Paragraph(
            "Controllers were evaluated under five scenarios: normal, noise, disturbance, slip, "
            "and combined. Metrics include RMSE tracking error, maximum tracking error, final "
            "tracking error, control effort, chattering index, and settling time. A headless "
            "benchmark compares all three controllers under identical conditions. A web-based "
            "3D digital twin (React + Three.js, FastAPI WebSocket backend) provides live "
            "visualization, replay, dual comparison, and CSV export.",
            styles["body"],
        )
    )
    add_figure(
        story, styles, "fig02_cnn_samples.png",
        "Figure 2 — Synthetic 64×64 environment maps used to train the CNN scenario classifier.",
        aspect=0.28,
    )
    story.append(PageBreak())


def _metric_table(story, styles):
    data = [
        ["Scenario", "RMSE Δ", "Final Error Δ", "Effort Δ", "Chattering Δ"],
        ["Normal", "0.00%", "0.00%", "0.00%", "0.00%"],
        ["Noise", "−10.98%", "−15.02%", "+6.89%", "−35.53%"],
        ["Disturbance", "+2.22%", "+36.96%", "−11.10%", "−12.22%"],
        ["Slip", "+1.57%", "+32.27%", "−12.83%", "−22.52%"],
        ["Combined", "−2.00%", "+2.16%", "−5.62%", "−27.67%"],
    ]
    table = Table(data, colWidths=[3.2 * cm, 2.4 * cm, 2.8 * cm, 2.4 * cm, 2.8 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d5c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f8fb")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(
        Paragraph(
            "Table 1 — Relative improvement of CNN-Adaptive SMC over Classical SMC "
            "(positive = adaptive better for error metrics; negative chattering = reduction).",
            styles["caption"],
        )
    )


def _benchmark_table(story, styles):
    data = [
        ["Controller", "Rank", "RMSE (m)", "Chattering", "Control Effort"],
        ["Classical SMC", "1", "0.245", "44.7", "527.7"],
        ["CNN-Adaptive SMC", "2", "0.260", "30.6", "549.4"],
        ["RL Agent (PPO)", "3", "0.265", "43.7", "581.9"],
    ]
    table = Table(data, colWidths=[4.5 * cm, 1.5 * cm, 2.5 * cm, 2.5 * cm, 3 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#145374")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(
        Paragraph(
            "Table 2 — Combined-scenario headless benchmark (noise + disturbance + slip, 12 s).",
            styles["caption"],
        )
    )


def section_results(story, styles):
    story.append(Paragraph("3. Results", styles["heading1"]))

    story.append(Paragraph("3.1 CNN Classification Performance", styles["heading2"]))
    story.append(
        Paragraph(
            "The environment CNN achieved <b>100% validation accuracy</b> on the synthetic "
            "64×64 map dataset after 12 training epochs (600 samples, 120 per class). "
            "This confirms that the perception pipeline correctly distinguishes scenario "
            "classes in the controlled dataset. Future work should validate on more realistic "
            "sensor maps derived from LiDAR or camera data.",
            styles["body"],
        )
    )
    add_figure(
        story, styles, "fig05_rmse_bars.png",
        "Figure 3 — RMSE tracking error comparison across all five operating scenarios.",
    )
    add_figure(
        story, styles, "fig06_chattering_bars.png",
        "Figure 4 — Chattering index comparison: CNN-adaptive SMC reduces oscillation in noisy conditions.",
    )

    story.append(Paragraph("3.2 Classical vs CNN-Adaptive SMC", styles["heading2"]))
    story.append(
        Paragraph(
            "Table 1 summarizes per-scenario improvements of CNN-adaptive SMC relative to "
            "classical SMC. Key findings:",
            styles["body"],
        )
    )
    findings = [
        "<b>Noisy conditions:</b> Chattering reduced by 35.5%, demonstrating smoother control, "
        "at the cost of higher RMSE (−11%) due to the tracking/smoothing trade-off.",
        "<b>Disturbance:</b> Final tracking error improved by 37.0% and RMSE by 2.2%, showing "
        "better post-disturbance recovery.",
        "<b>Slip:</b> Final error improved by 32.3% with modest RMSE gain (+1.6%).",
        "<b>Combined:</b> Chattering reduced by 27.7% with slight final-error improvement (+2.2%).",
    ]
    for item in findings:
        story.append(Paragraph(f"• {item}", styles["bullet"]))
    story.append(Spacer(1, 0.2 * cm))
    _metric_table(story, styles)

    add_figure(
        story, styles, "fig03_trajectory_comparison.png",
        "Figure 5 — Robot trajectories under combined uncertainty for all three controllers.",
    )
    add_figure(
        story, styles, "fig04_tracking_error.png",
        "Figure 6 — Tracking error over time: CNN-adaptive shows smoother error profile.",
    )
    story.append(PageBreak())

    story.append(Paragraph("3.3 Three-Controller Benchmark", styles["heading2"]))
    story.append(
        Paragraph(
            "Under the combined scenario, classical SMC achieved the lowest RMSE (0.245 m), "
            "while CNN-adaptive SMC achieved the lowest chattering index (30.6). The PPO agent "
            "achieved a best mean training reward of −0.766 after 20 iterations. RL performance "
            "is expected to improve with longer training and reward shaping; the current "
            "implementation demonstrates end-to-end integration rather than fully optimized policy.",
            styles["body"],
        )
    )
    _benchmark_table(story, styles)
    add_figure(
        story, styles, "fig07_controller_benchmark.png",
        "Figure 7 — Headless benchmark of Classical SMC, CNN-Adaptive SMC, and PPO RL Agent.",
        aspect=0.38,
    )

    story.append(Paragraph("3.4 Digital Twin Demonstration", styles["heading2"]))
    story.append(
        Paragraph(
            "The 3D digital twin successfully provides: live robot visualization in a hospital "
            "corridor environment, controller tour (Classical → CNN → RL), side-by-side dual "
            "comparison, simulation replay, and CSV export of metrics. The platform supports "
            "real-time WebSocket streaming at adjustable simulation speed (1×–5×), enabling "
            "effective presentation during project defense.",
            styles["body"],
        )
    )
    add_figure(
        story, styles, "fig08_digital_twin.png",
        "Figure 8 — Web-based 3D digital twin with live metrics dashboard (React + Three.js).",
        aspect=0.55,
    )


def section_conclusions(story, styles):
    story.append(Paragraph("4. Conclusions", styles["heading1"]))
    story.append(
        Paragraph(
            "This project designed, implemented, and evaluated a complete intelligent control "
            "pipeline for autonomous differential-drive robot navigation. Classical SMC provides "
            "a robust baseline; CNN-adaptive SMC adds scenario-aware parameter switching that "
            "significantly reduces chattering in noisy and combined conditions and improves "
            "recovery after disturbances and slip; the PPO RL agent provides a framework for "
            "continuous gain adaptation and was successfully integrated into the same simulation "
            "engine and digital twin.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "The main contribution is an end-to-end research platform — from synthetic dataset "
            "generation and CNN training, through multi-controller simulation and quantitative "
            "benchmarking, to an interactive 3D digital twin — suitable for AI Clinic demonstration "
            "and defense. Results confirm that adaptive control is not uniformly superior on every "
            "metric; instead, adaptation enables context-dependent trade-offs that are valuable "
            "in real deployments.",
            styles["body"],
        )
    )

    story.append(Paragraph("4.1 Future Work", styles["heading2"]))
    future = [
        "Replace synthetic maps with real LiDAR/camera occupancy grids.",
        "Extend RL training (more iterations, curriculum learning, reward tuning).",
        "Validate in physics simulators (Gazebo, PyBullet) and on a physical robot.",
        "Deploy the digital twin with live sensor feeds from a real platform.",
    ]
    for item in future:
        story.append(Paragraph(f"• {item}", styles["bullet"]))


def build_pdf(output: Path = OUTPUT_PATH):
    output.parent.mkdir(parents=True, exist_ok=True)
    ensure_figures()
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=REPORT_TITLE,
        author=", ".join(STUDENT_NAMES),
    )
    styles = _styles()
    story = []

    title_page(story, styles)
    section_intro(story, styles)
    section_methodology(story, styles)
    section_results(story, styles)
    section_conclusions(story, styles)

    doc.build(story)
    return output


if __name__ == "__main__":
    out = build_pdf()
    print(f"Report generated: {out}")
    if "[Supervisor Name" in SUPERVISOR_NAME:
        print("NOTE: Update SUPERVISOR_NAME and STUDENT_NAMES in this script before final submission.")
